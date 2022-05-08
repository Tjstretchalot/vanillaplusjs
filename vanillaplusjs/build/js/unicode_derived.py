"""This module includes  repeatable post-processing (assuming you have
the derived core property list from https://www.unicode.org/reports/tr44/#UCD_Files)
to produce the necessary unicode character properties for parsing javascript files
"""
from io import TextIOBase
from typing import Literal, Set, List, Tuple

from .derived_core_properties import (
    EXACT_MATCHES_ID_START,
    MATCH_RANGES_ID_START,
    EXACT_MATCHES_ID_CONTINUE,
    MATCH_RANGES_ID_CONTINUE,
)


def postprocess(
    derived_core_properties_fp: TextIOBase,
    out_fp: TextIOBase,
    property: Literal["ID_Start", "ID_Continue"],
) -> None:
    """Parses the derived core properties file to extract the necessary
    derived properties, and writes them as a python dictionary to the given
    output file.
    """

    expected_header_line = f"# Derived Property: {property}"
    while (line := derived_core_properties_fp.readline()) != "":
        if line.startswith(expected_header_line):
            break
    else:
        raise ValueError(f"Could not find header line {expected_header_line}")

    while (line := derived_core_properties_fp.readline()) != "":
        if not line.startswith("#"):
            break
    else:
        raise ValueError("Could not find any data lines")

    start_of_data = derived_core_properties_fp.tell()
    out_fp.write(f"EXACT_MATCHES_{property.upper()} = frozenset(\n")
    out_fp.write("    '")
    while (line := derived_core_properties_fp.readline()) != "":
        if not line.strip():
            break

        relevant_part = line.split(";", maxsplit=1)[0].strip()

        if ".." not in relevant_part:
            out_fp.write("\\u")
            out_fp.write(relevant_part)

    derived_core_properties_fp.seek(start_of_data)
    out_fp.write(f"'\n)\n\nMATCH_RANGES_{property.upper()} = (\n   ")

    num_since_last_newline = 0
    while (line := derived_core_properties_fp.readline()) != "":
        if not line.strip():
            break

        relevant_part = line.split(";", maxsplit=1)[0].strip()

        if ".." in relevant_part:
            start_range, end_range = relevant_part.split("..")
            out_fp.write(f" (0x{start_range}, 0x{end_range}),")
            num_since_last_newline += 1

            if num_since_last_newline > 5:
                out_fp.write("\n   ")
                num_since_last_newline = 0

    if num_since_last_newline:
        out_fp.write("\n")
    out_fp.write(")\n")


def is_match(
    char: str, exact_matches: Set[str], match_ranges: List[Tuple[int, int]]
) -> bool:
    """Determines if the given char matches either any of the exact matches
    or one of the match ranges.
    """
    if char in exact_matches:
        return True

    left = 0
    right = len(match_ranges) - 1
    needle = ord(char)
    while left <= right:
        mid = (left + right) // 2

        if match_ranges[mid][0] <= needle <= match_ranges[mid][1]:
            return True

        if needle < match_ranges[mid][0]:
            right = mid - 1
        else:
            left = mid + 1

    return False


def is_id_start(char: str) -> bool:
    """Determines if the given char is an ID_Start character."""
    return is_match(char, EXACT_MATCHES_ID_START, MATCH_RANGES_ID_START)


def is_id_continue(char: str) -> bool:
    """Determines if the given char is an ID_Continue character."""
    return is_match(char, EXACT_MATCHES_ID_CONTINUE, MATCH_RANGES_ID_CONTINUE)


if __name__ == "__main__":
    import os

    if not os.path.exists("DerivedCoreProperties.txt"):
        print("Rerun with DerivedCoreProperties.txt in the same directory")
        raise SystemExit(1)

    with open("vanillaplusjs/build/js/derived_core_properties.py", "w") as out_fp:
        with open("DerivedCoreProperties.txt", "r") as fp:
            postprocess(fp, out_fp, "ID_Start")
            out_fp.write("\n")
        with open("DerivedCoreProperties.txt", "r") as fp:
            postprocess(fp, out_fp, "ID_Continue")
            out_fp.write("\n")
