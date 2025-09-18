import os
import sys


def check_files(directory: str, target_language: str):
    """
    Checks each file in the given directory to verify whether it contains
    the specified target language header in the format: #Language#.

    Args:
        directory (str): The directory containing translated files.
        target_language (str): The target language name (e.g., "English", "Serbian").
    """
    header = f"#{target_language}#".lower()
    missing_header_files = []

    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Only check files (skip subdirectories)
        if not os.path.isfile(file_path):
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if header not in content.lower():
                    missing_header_files.append(filename)
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    # Report results
    if missing_header_files:
        print("Files missing the target language header:")
        for f in missing_header_files:
            print(f" - {f}")
    else:
        print(f"✅ All files contain the header '{header}'")

    return missing_header_files


def delete_missing_files(directory: str, missing_header_files: list[str]) -> None:
    """
    Deletes files from the given directory that are listed in missing_header_files.

    Args:
        directory (str): The directory containing the files.
        missing_header_files (list[str]): List of filenames that should be deleted.
    """
    if not missing_header_files:
        print("No files to delete. All files had the target header.")
        return

    for filename in missing_header_files:
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️ Deleted: {filename}")
            except Exception as e:
                print(f"⚠️ Could not delete {filename}: {e}")
        else:
            print(f"⚠️ File not found or is not a regular file: {filename}")


if __name__ == "__main__":
    # if len(sys.argv) < 3:
    #     print("Usage: python file_checker.py <directory> <target_language>")
    #     print("Example: python file_checker.py translated_pages English")
    #     sys.exit(1)
    #
    # directory = sys.argv[1]
    # target_language = sys.argv[2]
    # check_files(directory, target_language)
    missing_translation_files = check_files("../data/GL-9_Print Ready/translated_pages", "German")
    delete_missing_files("../data/GL-9_Print Ready/translated_pages", missing_translation_files)


