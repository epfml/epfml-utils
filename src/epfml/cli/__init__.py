import argparse
import contextlib
import sys

import epfml.cli.bundle as bundle
import epfml.cli.store as store
import epfml.cli.subcommand as subcommand


def main():
    commands: list[subcommand.SubCommand] = [store.Store(), bundle.Bundle()]

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
