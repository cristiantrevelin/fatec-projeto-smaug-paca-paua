from zipfile import ZipFile
import os
import shutil


def get_file_paths(directory):

    file_paths = list()

    for root, directories, files in os.walk(directory):
        for file in files:

            file_path = os.path.join(root, file)
            file_paths.append(file_path)

    return file_paths


def compress_dir(paths, compressed_name, uncompressed_dir):

    with ZipFile(f'{compressed_name}.zip', 'w') as compressor:
        for file in paths:
            compressor.write(file)

        compressor.close()

    shutil.rmtree(uncompressed_dir)


def extract_dir(compressed_dir):

    with ZipFile(f'{compressed_dir}.zip', 'r') as decompressor:
        decompressor.extractall()

    os.remove(f'{compressed_dir}.zip')
