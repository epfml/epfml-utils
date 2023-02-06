import argparse
import contextlib
import pathlib
import subprocess
import sys
import tempfile
from typing import Protocol

import toml

import epfml.bundle as bundle
import epfml.config as config
import epfml.store as store
import epfml.vpn as vpn


def main():
    commands: list[SubCommand] = [Store(), Bundle()]

    with _nicely_print_runtime_errors():
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command", required=True)

        for command in commands:
            command.define_parser(subparsers.add_parser(command.name))

        args = parser.parse_args()

        for command in commands:
            if args.command == command.name:
                return command.main(args)

        raise RuntimeError(f"Unsupported command {args.command}.")


class SubCommand(Protocol):
    name: str

    def define_parser(self, parser: argparse.ArgumentParser):
        ...

    def main(self, args: argparse.Namespace):
        ...


class Store(SubCommand):
    name = "store"

    def define_parser(self, parser):
        parser.add_argument("--user", "-u", type=str, default=config.ldap)

        subparsers = parser.add_subparsers(dest="subcommand", required=True)

        getparser = subparsers.add_parser("get")
        getparser.add_argument("key", type=str)

        unsetparser = subparsers.add_parser("unset")
        unsetparser.add_argument("key", type=str)

        setparser = subparsers.add_parser("set")
        setparser.add_argument("key", type=str)
        setparser.add_argument("value", type=str)

    def main(self, args):
        vpn.assert_connected()

        if args.subcommand == "get":
            print(store.get(args.key, user=args.user))

        elif args.subcommand == "set":
            store.set(args.key, args.value, user=args.user)

        elif args.subcommand == "unset":
            store.unset(args.key, user=args.user)


class Bundle(SubCommand):
    name = "bundle"

    def define_parser(self, parser):
        parser.add_argument("--user", "-u", type=str, default=config.ldap)

        subparsers = parser.add_subparsers(dest="subcommand", required=True)

        packparser = subparsers.add_parser("pack")
        packparser.add_argument("directory", type=pathlib.Path, nargs="?")

        unpackparser = subparsers.add_parser("unpack")
        unpackparser.add_argument("package_id", type=str, help="The package to unpack.")
        unpackparser.add_argument(
            "-o",
            "--output",
            type=pathlib.Path,
            default=".",
            help="The output directory.",
        )

        execparser = subparsers.add_parser("exec")
        execparser.add_argument("--directory", "-d", type=pathlib.Path, default=None)
        execparser.add_argument("package_id", type=str, help="The package to unpack.")
        execparser.add_argument(
            "cmd",
            type=str,
            nargs="+",
            help="The command to execute in the checked out package.",
        )

        initparser = subparsers.add_parser(
            "init", help="Create a .epfml.bundle.toml file."
        )
        initparser.add_argument(
            "-f", "--force", action="store_true", help="Overwrite existing config file."
        )
        initparser.add_argument("directory", type=pathlib.Path, nargs="?")

    def main(self, args):
        vpn.assert_connected()

        if args.subcommand == "pack":
            if args.directory is None:
                args.directory = pathlib.Path.cwd()

            package = bundle.tar_package(args.directory)
            store.set(f"bundle/{package.id}", package.contents, user=args.user)

            print(f"📦 Packaged and shipped.")
            print(f"⬇️  Unpack with `epfml bundle unpack {package.id} -o .`.")

        elif args.subcommand == "unpack":
            byte_content = store.get(f"bundle/{args.package_id}", user=args.user)
            bundle.tar_extract(byte_content, args.output)
            print(f"📦 Delivered to `{args.output}`.", file=sys.stderr)

        elif args.subcommand == "exec":
            byte_content = store.get(f"bundle/{args.package_id}", user=args.user)

            def run_in(directory):
                bundle.tar_extract(byte_content, directory)
                subprocess.run(" ".join(args.cmd), cwd=directory, shell=True)

            if args.directory is not None:
                print(
                    f"🏃 Running in directory `{args.directory}` ({args.package_id}).",
                    file=sys.stderr,
                )
                run_in(args.directory)
            else:
                print(
                    f"🏃 Running inside a tmp clone of package `{args.package_id}`.",
                    file=sys.stderr,
                )
                with tempfile.TemporaryDirectory() as tmpdir:
                    run_in(tmpdir)

        elif args.subcommand == "init":
            if args.directory is None:
                args.directory = pathlib.Path.cwd()

            if not args.directory.is_dir():
                raise RuntimeError("Not a directory.")
            config_path = args.directory / bundle.CONFIG_FILENAME
            if not args.force and config_path.is_file():
                raise RuntimeError(f"A `{bundle.CONFIG_FILENAME}` file already exists.")
            with open(config_path, "w") as f:
                toml.dump(bundle.DEFAULT_CONFIG, f)
            print(f"📦 Default config file written to `{config_path}`.", file=sys.stderr)


@contextlib.contextmanager
def _nicely_print_runtime_errors():
    try:
        yield
    except RuntimeError as e:
        print(_red_background(" Error "), e, file=sys.stderr)
        sys.exit(1)


def _red_background(text: str) -> str:
    return "\033[41m" + text + "\033[0m"


if __name__ == "__main__":
    main()
