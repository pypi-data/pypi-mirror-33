#!/usr/bin/env python3
"""Source code for anotherpdfmerger."""

import argparse
import os
import time
import PyPDF2
from anotherpdfmerger.version import NAME, VERSION, DESCRIPTION

def main():
    """Main function for anotherpdfmerger."""
    # Get runtime args
    runtimeargs = parse_runtime_args()

    # Generate bookmark names
    bkmarks = [os.path.basename(path) for path in runtimeargs.sources]
    bkmarks = [os.path.splitext(name)[0] for name in bkmarks]

    # Now merge the files and insert bookmarks
    newpdf = PyPDF2.PdfFileMerger()
    for x in enumerate(zip(runtimeargs.sources, bkmarks)):
        newpdf.append(x[1][0], bookmark=x[1][1])

    # Write to the output file
    newpdf.write(runtimeargs.destination)


def parse_runtime_args():
    """Parse runtime args using argparse.

    Returns:
        An object of type 'argparse.Namespace' containing the runtime
        arguments as attributes. See argparse documentation for more
        details.
    """
    parser = argparse.ArgumentParser(
            prog=NAME,
            description="%(prog)s - " + DESCRIPTION,)

    parser.add_argument(
            "sources",
            nargs='+',
            type=str,
            help="path to source PDFs")
    parser.add_argument(
            "destination",
            type=str,
            default=time.strftime("%Y%m%d_%H%M_%S_merge.pdf"),
            help="path to destination PDF")
    parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s " + VERSION)

    return parser.parse_args()
