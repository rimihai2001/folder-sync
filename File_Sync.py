import os
import time
import hashlib
import argparse

def log_message(message):
    current_time = time.strftime('%d-%m-%Y %H:%M:%S')
    log.write(f"[{current_time}] {message}\n")
    log.flush()
    print(message)

def compute_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        while (chunk := file.read(8192)):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def copy_file(source_path, destination_folder):
    try:
        not_dup = 1
        source_hash = compute_file_hash(source_path)

        for root, _, files in os.walk(destination_folder):
            for file in files:
                destination_path = os.path.join(root, file)
                if source_hash == compute_file_hash(destination_path) and os.path.basename(source_path) not in os.listdir(destination_folder):
                    log_message(f"File '{source_path[source_path.index('/') + 1:]}' is a duplicate of '{destination_path[destination_path.index('/') + 1:]}'")
                    not_dup = 0
                    

        source_filename = os.path.basename(source_path)
        destination_path = os.path.join(destination_folder, source_filename)
        with open(source_path, 'rb') as source_file, open(destination_path, 'wb') as copy_file:
                copy_file.write(source_file.read())
  
        if not_dup == 1:
            log_message(f"{source_path[source_path.index('/') + 1:]} added/updated")
        else:
            log_message(f"{source_path[source_path.index('/') + 1:]} added as a copy of {destination_path[destination_path.index('/') + 1:]}")
    except Exception as e:
        log_message(f"Error copying file: {e}")

def copy_folder(source, destination):
    try:
        if not os.path.exists(destination):
            os.makedirs(destination)

        source_files = os.listdir(source)
        destination_files = os.listdir(destination)

        to_del = []

        for f in destination_files:
            if f not in source_files:
                to_del.append(f)

        for file_to_delete in to_del:
            file_to_delete_path = os.path.join(destination, file_to_delete)
            os.remove(file_to_delete_path)
            log_message(f"{file_to_delete_path[file_to_delete_path.index('/') + 1:]} has been deleted")

        for item in source_files:
            source_item = os.path.join(source, item)
            destination_item = os.path.join(destination, item)

            if os.path.isdir(source_item):
                copy_folder(source_item, destination_item)
            else:
                copy_file(source_item, destination)

        log_message(f"Folder synced: {source} to {destination}")
    except Exception as e:
        log_message(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Folders")
    parser.add_argument("--source", required=True, help="Path to the source folder")
    parser.add_argument("--destination", required=True, help="Path to the destination folder")
    parser.add_argument("--interval", type=int, default=600, help="Synchronization interval in seconds")
    parser.add_argument("--file", default="sync_log.txt", help="Path to the log file")
    args = parser.parse_args()

    source_folder = args.source
    destination_folder = args.destination
    log_file = args.file

    log = open(log_file, 'a')

    while True:
        try:
            copy_folder(source_folder, destination_folder)
        except Exception as e:
            log_message(f"An error occurred: {e}")
            break
        time.sleep(args.interval)

    log.close()
