import os
from pathlib import Path
from typing import List
import argparse
from typing import Any



def find_python_files(base_path: Path) -> List[Path]:
    """
    Recursively find all Python files in the given directory.
    """
    python_files: List[Path] = []

    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py"):
                full_path = Path(root) / file
                python_files.append(full_path)

    return python_files


def get_relative_path(base_path: Path, file_path: Path) -> Path:
    """
    Return the relative path from base_path to file_path.
    """
    return file_path.relative_to(base_path)


def read_file_content(file_path: Path) -> str:
    """
    Read the content of a file safely.
    """
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return f.read()
    except Exception as error:
        return f"ERROR READING FILE: {error}"


def write_output(
    base_path: Path,
    python_files: List[Path],
    output_file: Path
) -> None:
    """
    Write all file paths and contents into a single output file.
    """
    with output_file.open("w", encoding="utf-8") as out:
        for file_path in python_files:
            relative_path = get_relative_path(base_path, file_path)
            content = read_file_content(file_path)

            out.write(f"{relative_path}:\n")
            out.write(content)
            out.write("\n\n")


def parse_args() -> Any:
    parser = argparse.ArgumentParser(
        description="Collect all .py files and write their content into one file."
    )

    parser.add_argument(
        "input_dir",
        type=str,
        help="Input directory to scan"
    )

    parser.add_argument(
        "output_file",
        type=str,
        help="Output file path"
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("RAW INPUT:", args.input_dir)
    print("RESOLVED:", Path(args.input_dir).resolve())
    print("EXISTS:", Path(args.input_dir).exists())
    print("IS DIR:", Path(args.input_dir).is_dir())

    base_directory = Path(args.input_dir).resolve()
    output_file = Path(args.output_file).resolve()

    if not base_directory.exists() or not base_directory.is_dir():
        print("Invalid input directory:", base_directory)
        return

    python_files = find_python_files(base_directory)

    if not python_files:
        print("No Python files found")
        return

    write_output(base_directory, python_files, output_file)

    print(f"Done. Output written to {output_file}")


if __name__ == "__main__":
    main()
