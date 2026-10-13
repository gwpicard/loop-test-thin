import argparse


def build_parser():
    parser = argparse.ArgumentParser(prog="habits", description="Habit tracker.")
    # Later pieces add sub-commands here: subparsers.add_parser("add"), and so on.
    parser.add_subparsers(dest="command", metavar="command", required=True)
    return parser


def main(argv=None):
    build_parser().parse_args(argv)
    return 0
