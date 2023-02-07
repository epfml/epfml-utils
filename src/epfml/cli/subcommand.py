import argparse
from typing import Protocol


class SubCommand(Protocol):
    name: str

    def define_parser(self, parser: argparse.ArgumentParser):
        ...

    def main(self, args: argparse.Namespace):
        ...
