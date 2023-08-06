import sys
import os


def main():
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    import ecf_parser

    src_file = sys.argv[2]
    if sys.argv[1] == "to-json":
        for line in ecf_parser.ecf_file_to_json(src_file):
            print(line)
    elif sys.argv[1] == "to-ecf":
        for entry in ecf_parser.jsonl_file_to_ecf(src_file):
            print(entry)


if __name__ == "main":
    main()