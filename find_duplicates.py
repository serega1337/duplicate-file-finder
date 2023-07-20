import argparse
import os
import hashlib
import sys
from tqdm import tqdm


class DuplicateFileFinder:
    def __init__(self, output_file):
        self.hashes = {}
        self.output_file = output_file

    def get_file_hash(self, file_path):
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        return file_hash.hexdigest()

    def process_file(self, file_path):
        file_name = os.path.basename(file_path)
        file_hash = self.get_file_hash(file_path)
        if file_hash in self.hashes:
            result = f"Found identical files: {self.hashes[file_hash]} and {file_name}"
            print(result)
            self.output_file.write(result + "\n")
        else:
            self.hashes[file_hash] = file_name

    def process_files(self, files_to_process):
        for file_path in tqdm(files_to_process):
            self.process_file(file_path)


def collect_files(paths, types=None):
    files_to_process = []
    for path in paths:
        if os.path.isfile(path):
            if not types or any(path.endswith(t) for t in types):
                files_to_process.append(path)
        elif os.path.isdir(path):
            print(f"Processing folder: {path}")
            for file_name in os.listdir(path):
                file_path = os.path.join(path, file_name)
                if os.path.isfile(file_path) and (not types or any(file_path.endswith(t) for t in types)):
                    files_to_process.append(file_path)
        else:
            print(f'Error: "{path}" is not a valid file or directory.')
    return files_to_process


def main():
    parser = argparse.ArgumentParser(
        description="Find identical files")
    parser.add_argument("initial_paths", nargs="*",
                        help="Folders or files to be processed.")
    parser.add_argument("--paths", nargs="*",
                        help="Folders or files to be processed.")
    parser.add_argument("--types", "-t", nargs="*",
                        help="Select only specific file types.")
    parser.add_argument("-o", "--output", default="result.txt",
                        help="Path to the output file (default: result.txt)")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    try:
        all_paths = list(set(args.initial_paths + (args.paths or [])))
        files_to_process = collect_files(all_paths, args.types)
        if not files_to_process:
            print("No files to process.")
            sys.exit(0)

        output_file = open(args.output, "w")
        duplicate_finder = DuplicateFileFinder(output_file)
        duplicate_finder.process_files(files_to_process)

        output_file.close()
    except KeyboardInterrupt:
        print("\nInterrupt signal received")
        if output_file:
            output_file.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
