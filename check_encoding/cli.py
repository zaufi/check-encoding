#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Alex Turbov <zaufi@pm.me>
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import os
import sys
import codecs
from encodings.aliases import aliases
from functools import reduce


def die(message: str) -> None:
    """Print an error message prefixed with a red cross."""
    print(f"❌ {message}", file=sys.stderr)


def iter_existing_files(paths):
    """Yield only existing files and report missing ones."""
    iter_existing_files.missing = False
    for path in paths:
        if os.path.isfile(path):
            yield path
        else:
            iter_existing_files.missing = True
            die(f"{path}: File not found")


def list_encodings():
    """Print all known encodings and their aliases in aligned columns"""
    canonical_to_aliases = reduce(
        lambda m, ai: m | {ai[1]: m.get(ai[1], []) + [ai[0]]}, aliases.items(), {}
    )
    canonical_to_aliases = {
        canonical: list(dict.fromkeys(alist))
        for canonical, alist in canonical_to_aliases.items()
    }

    for canonical, alias_list in canonical_to_aliases.items():
        print(f"{canonical.ljust(15)} (aliases: {', '.join(alias_list)})")


def check_file_encoding(filepath, decoder, max_errors=10):
    try:
        with open(filepath, "rb") as f:
            data = f.read()
    except Exception as e:
        die(f"{filepath}: Could not read file: {e}")
        return False

    line = 1
    column = 1
    i = 0
    errors = 0

    decoder.reset()
    while i < len(data):
        byte = data[i : i + 1]
        try:
            decoded = decoder.decode(byte, final=False)
            if decoded == "\n":
                line += 1
                column = 1
            elif decoded:
                column += 1
            i += 1
        except UnicodeDecodeError:
            hexval = f"0x{data[i]:02X}"
            die(f"{filepath}:{line}:{column} Invalid character {hexval}")
            errors += 1
            if errors >= max_errors:
                break
            i += 1
            column += 1

    return errors == 0


def main():
    parser = argparse.ArgumentParser(
        description="Check if files are in a specific encoding (default: UTF-8)."
    )
    parser.add_argument("files", nargs="*", help="Files to check")
    parser.add_argument(
        "--encoding", default="utf-8", help="Encoding to check against (default: utf-8)"
    )
    parser.add_argument(
        "--max-errors",
        type=int,
        default=10,
        help="Maximum number of errors to report per file (default: 10)",
    )
    parser.add_argument(
        "--list-encodings",
        action="store_true",
        help="List all supported encoding names",
    )

    args = parser.parse_args()

    if args.list_encodings:
        list_encodings()
        sys.exit(0)

    if not args.files:
        parser.print_help()
        sys.exit(1)

    try:
        decoder_cls = codecs.getincrementaldecoder(args.encoding)
        decoder = decoder_cls(errors="strict")
    except LookupError:
        die(f"Unknown encoding: {args.encoding}")
        sys.exit(1)

    found_error = reduce(
        lambda rs, f: not check_file_encoding(f, decoder, args.max_errors) or rs,
        iter_existing_files(args.files),
        False,
    )
    found_error = found_error or iter_existing_files.missing

    sys.exit(int(found_error))
