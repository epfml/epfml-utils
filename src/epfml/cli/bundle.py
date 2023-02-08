import argparse
import os
import pathlib
import subprocess
import sys
import tempfile

import toml

import epfml.bundle as bundle
import epfml.config as config
import epfml.store as store
import epfml.vpn as vpn
from epfml.cli.subcommand import SubCommand


class Bundle(SubCommand):
    name = "bundle"

    def __init__(self):
        self._actions = [
            Pack(),
            Unpack(),
            Exec(),
            Init(),
        ]

    def define_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("--user", "-u", type=str, default=config.ldap)

        subparsers = parser.add_subparsers(dest="action", required=True)
        for action in self._actions:
            action_parser = subparsers.add_parser(action.name)
            action.define_parser(action_parser)

    def main(self, args):
        vpn.assert_connected()
        config.assert_store_is_configured()

        for action in self._actions:
            if args.action == action.name:
                return action.main(args)

        raise RuntimeError(f"Unsupported action {args.action}.")


class Pack(SubCommand):
    name = "pack"

    def define_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("directory", type=pathlib.Path, nargs="?")

    def main(self, args):
        if args.directory is None:
            args.directory = pathlib.Path.cwd()

        package = bundle.tar_package(args.directory)
        store.set(f"bundle/{package.id}", package.contents, user=args.user)

        print(f"📦 Packaged and shipped.", file=sys.stderr)
        print(
            f"⬇️  Unpack with `epfml bundle unpack {package.id} -o .`.", file=sys.stderr
        )
        print(package.id)


class Unpack(SubCommand):
    name = "unpack"

    def define_parser(self, parser):
        parser.add_argument("bundle_id", type=str, help="The package to unpack.")
        parser.add_argument(
            "-o",
            "--output",
            type=pathlib.Path,
            default=".",
            help="The output directory.",
        )

    def main(self, args):
        byte_content = store.get(f"bundle/{args.bundle_id}", user=args.user)
        bundle.tar_extract(byte_content, args.output)
        print(f"📦 Delivered to `{args.output}`.", file=sys.stderr)


class Exec(SubCommand):
    name = "exec"

    def define_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("--directory", "-d", type=pathlib.Path, default=None)
        parser.add_argument(
            "--as-ldap",
            action="store_true",
            default=False,
            help="Run as the LDAP user.",
        )
        parser.add_argument("bundle_id", type=str, help="The package to unpack.")
        parser.add_argument(
            "cmd",
            type=str,
            nargs="+",
            help="The command to execute in the checked out package.",
        )

    def main(self, args):
        byte_content = store.get(f"bundle/{args.bundle_id}", user=args.user)

        def run_in(directory):
            bundle.tar_extract(byte_content, directory)
            try:
                subprocess.run(
                    " ".join(args.cmd),
                    cwd=directory,
                    shell=True,
                    user=config.ldap if args.as_ldap else None,
                    check=True,
                    env={**os.environ, "EPFML_BUNDLE_ID": args.bundle_id},
                )
            except KeyError:
                raise RuntimeError(f"LDAP user `{config.ldap}` not found.")

        if args.directory is not None:
            print(
                f"🏃 Running in directory `{args.directory}` ({args.bundle_id}).",
                file=sys.stderr,
            )
            run_in(args.directory)
        else:
            print(
                f"🏃 Running inside a tmp clone of bundle `{args.bundle_id}`.",
                file=sys.stderr,
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                run_in(tmpdir)


class Init(SubCommand):
    name = "init"

    def define_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "-f", "--force", action="store_true", help="Overwrite existing config file."
        )
        parser.add_argument("directory", type=pathlib.Path, nargs="?")

    def main(self, args):
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
