import argparse
import os
import hashlib
import sys
from tqdm import tqdm
from collections import defaultdict


class DuplicateFileFinder:
    def __init__(self, output_file):
        self.hashes = defaultdict(list)
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
        self.hashes[file_hash].append(file_path)
        if len(self.hashes[file_hash]) > 1:
            print(f"Found duplicate file: {file_name}")

    def process_files(self, files_to_process):
        for file_path in tqdm(files_to_process):
            self.process_file(file_path)
        self.write_duplicates_to_output()

    def write_duplicates_to_output(self):
        for file_hash, file_paths in self.hashes.items():
            if len(file_paths) < 2:
                continue
            self.output_file.write(f"Duplicate files:\n")
            for file_path in file_paths:
                self.output_file.write(f"\t{os.path.abspath(file_path)}\n")

    def delete_duplicates(self):
        for file_hash, file_paths in self.hashes.items():
            if len(file_paths) < 2:
                continue
            for file_path in file_paths[1:]:
                file_name = os.path.basename(file_path)
                os.remove(file_path)
                print(f"Deleted: {file_name}")


def collect_files(paths, types, output_file):
    files_to_process = set()
    for path in paths:
        if os.path.isfile(path):
            if not types or any(path.endswith(t) for t in types):
                files_to_process.add(path)
        elif os.path.isdir(path):
            processing_folder_message = f"Processing folder: {os.path.abspath(path)}"
            print(processing_folder_message)
            output_file.write(processing_folder_message + "\n")
            for file_name in os.listdir(path):
                file_path = os.path.join(path, file_name)
                if os.path.isfile(file_path) and (not types or any(file_path.endswith(t) for t in types)):
                    files_to_process.add(file_path)
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
        output_file = open(args.output, "w")
        files_to_process = collect_files(all_paths, args.types, output_file)
        if not files_to_process:
            print("No files to process.")
            sys.exit(0)

        duplicate_finder = DuplicateFileFinder(output_file)
        duplicate_finder.process_files(files_to_process)
        confirm_delete_files = input("Delete the duplicate files? (y/n): ")
        if confirm_delete_files.lower() == 'y':
            duplicate_finder.delete_duplicates()

        output_file.close()
    except KeyboardInterrupt:
        print("\nInterrupt signal received")
        if output_file:
            output_file.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
