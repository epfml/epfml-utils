import argparse
import contextlib
import sys
from typing import Protocol

import epfml.config as config
import epfml.store as store
import epfml.vpn as vpn


def main():
    commands: list[SubCommand] = [Store()]

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
        parser.add_argument("--user", "-u", type=str, default=config.default_user)

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
            store.set(args.key, args.value, user=args.user, ttl="1d")
        elif args.subcommand == "unset":
            store.unset(args.key, user=args.user)


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
