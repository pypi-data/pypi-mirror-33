#!/usr/bin/env python
# coding: utf-8
"""
RIP tr/sed. Python regex replacement utility.
"""
from __future__ import print_function
import argparse
import difflib
import re
import sys

__version__ = "1.2.2"


def output_unified_diff(olddata, newdata, oldfile):
    """Output unified diff from old->new"""
    del oldfile
    print(
        "\n".join(
            difflib.unified_diff(
                olddata.splitlines(), newdata.splitlines(), lineterm=""
            )
        )
    )


def output_stdout(olddata, newdata, oldfile):
    """Output result to stdout"""
    del olddata, oldfile
    print(newdata)


def output_inplace(olddata, newdata, oldfile):
    """Output result to file-like"""
    del olddata
    with open(oldfile, "w") as outfile:
        outfile.write(newdata)


def output_none(olddata, newdata, oldfile):
    """No output"""
    del olddata, newdata, oldfile


def main():
    """Run some regex substitutions on cmd line files"""
    parser = argparse.ArgumentParser(
        description="Rip tr v{VERSION}".format(VERSION=__version__)
    )
    parser.add_argument(
        "file",
        metavar="FILE",
        type=str,
        nargs="+",
        help=(
            'Input file(s). Combine with -w to speed this up, eg "riptr '
            '-m <match> -s <sub> -w $(ls <dir>)"'
        ),
    )
    parser.add_argument(
        "-m",
        "--match",
        metavar="REGEX",
        type=str,
        help="Matching regex, python syntax",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--substitute",
        metavar="REGEX",
        type=str,
        help="Substitute regex, python syntax; backref groups per the --match arg.",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--outputmode",
        choices=["inplace", "i", "patch", "p", "stdout", "s"],
        help="Set output mode- inplace/i = edit in place, patch/p = generate unified patch",
        default="stdout",
    )
    parser.add_argument(
        "-d", "--dotall", action="store_true", help="Set dotall on the regex"
    )
    parser.add_argument(
        "-l", "--multiline", action="store_true", help="Set multiline on the regex"
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="Print version and exit"
    )
    args = parser.parse_args()

    flags = 0
    if args.dotall:
        flags += re.DOTALL
    if args.multiline:
        flags += re.MULTILINE

    matcher = re.compile(args.match, flags=flags)

    for fname in args.file:
        outputter = args.outputmode
        if fname == "-":
            if not sys.stdin.isatty():
                indata = sys.stdin.read()
                if outputter == "i" or outputter == "inplace":
                    outputter = None
            else:
                # nothing on stdin 💁
                continue
        else:
            with open(fname, "r") as infile:
                indata = infile.read()

        # perform the substitution
        outdata = matcher.sub(args.substitute, indata)

        # Map of outputters
        outputters = {
            "inplace": output_inplace,
            "i": output_inplace,
            "patch": output_unified_diff,
            "p": output_unified_diff,
            "stdout": output_stdout,
            "s": output_stdout,
            None: output_none,
        }
        # Output result
        outputters[outputter](indata, outdata, fname)


if __name__ == "__main__":
    main()
