#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Alex Turbov <zaufi@pm.me>
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import sys
import os
import codecs
from collections import defaultdict
from encodings.aliases import aliases
from functools import reduce


def iter_existing_files(paths):
    """Yield only existing files and report missing ones."""
    iter_existing_files.missing = False
    for path in paths:
        if os.path.isfile(path):
            yield path
        else:
            iter_existing_files.missing = True
            print(f"❌ {path}: File not found", file=sys.stderr)


def list_encodings():
    """Print all known encodings and their aliases in aligned columns"""
    canonical_to_aliases = defaultdict(list)
    for alias, canonical in aliases.items():
        canonical_to_aliases[canonical].append(alias)

    for canonical in sorted(canonical_to_aliases.keys()):
        alias_list = sorted(set(canonical_to_aliases[canonical]))
        print(f"{canonical.ljust(15)} (aliases: {', '.join(alias_list)})")


def check_file_encoding(filepath, encoding, max_errors=10):
    try:
        with open(filepath, "rb") as f:
            data = f.read()
    except Exception as e:
        print(f"❌ {filepath}: Could not read file: {e}", file=sys.stderr)
        return False

    try:
        decoder = codecs.getincrementaldecoder(encoding)(errors="strict")
    except LookupError:
        print(f"❌ Unknown encoding: {encoding}", file=sys.stderr)
        return False

    line = 1
    column = 1
    i = 0
    errors = 0

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
            print(
                f"❌ {filepath}:{line}:{column} Invalid character {hexval}",
                file=sys.stderr,
            )
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
        codecs.lookup(args.encoding)
    except LookupError:
        print(f"❌ Unknown encoding: {args.encoding}", file=sys.stderr)
        sys.exit(1)

    found_error = reduce(
        lambda acc, file: acc
        or not check_file_encoding(file, args.encoding, args.max_errors),
        iter_existing_files(args.files),
        False,
    )
    found_error = found_error or iter_existing_files.missing

    sys.exit(int(found_error))
