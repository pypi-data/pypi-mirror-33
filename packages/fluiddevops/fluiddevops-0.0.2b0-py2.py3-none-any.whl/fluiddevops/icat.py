import argparse
import fileinput
import sys


def get_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Intermittent cat command. Watch stdin or catenate a set of files"
            "and output to stdout for every N lines"
        )
    )
    parser.add_argument("-e", "--every", type=int, default=5)
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        help="files to read, if empty, stdin is used",
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    # If you would call fileinput.input() without files it would try to process all arguments.
    # We pass '-' as only file when argparse got no files which will cause fileinput to read from stdin
    i = 0
    for line in fileinput.input(args.files):
        i += 1
        if i % args.every == 0:
            print(line, end="")


if __name__ == "__main__":
    main()
