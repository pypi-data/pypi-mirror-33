"""The nes-py NES emulator."""
from argparse import ArgumentParser


def get_args() -> ArgumentParser:
    """Create and return an argument parser for this command line interface."""
    # create an argument parsers to read command line options
    parser = ArgumentParser(description=__doc__)
    # parse the arguments
    args = parser.parse_args()

    return args


def main() -> None:
    """The main entry point for the command line interface."""
    # parse validated arguments from the command line
    args = get_args()


# explicitly define the outward facing API of this module
__all__ = [main.__name__]
