"""Console script for xmlsplitter."""
import argparse
import sys

from .xmlsplitter import XMLSplitParser

def main():
    """Console script for xmlsplitter."""
    parser = argparse.ArgumentParser(description="Split an XML file")
    parser.add_argument("xml_filepath", nargs="?", help="path to xml to be split")
    parser.add_argument("-o", "--output-dir", action="store", type=str,
                        help="directory to store all created files in")
    parser.add_argument(
        "-M",
        "--max-size",
        type=int,
        help="Specify the size at which the files should be split (in Kb)",
    )
    parser.add_argument(
        "-D",
        "--split-depth",
        type=int,
        help="Specify the tree depth at which file splits are allowed to occur",
    )
    args = parser.parse_args()

    if args.max_size is not None:
        args.max_size *= 1024
    xmlsplit = XMLSplitParser(
        args.xml_filepath, args.output_dir, args.max_size, args.split_depth
    )
    xmlsplit.parse()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover


