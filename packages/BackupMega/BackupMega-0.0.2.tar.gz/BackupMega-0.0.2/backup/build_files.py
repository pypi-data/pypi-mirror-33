import logging
import os
import zipfile
from os import path
from zipfile import ZipFile

logging.basicConfig(level=logging.DEBUG)


def zip_folder(folder_paths: list, output_path: str):
    """Zip the contents of an entire folder (with that folder included
    in the archive). Empty subfolders will be included in the archive
    as well.
    """
    os.system('rm -rf {}/*'.format(os.path.dirname(output_path)))
    if not os.path.exists('/tmp/backup'):
        os.system('mkdir /tmp/backup')
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for folder_path in folder_paths:
            if not os.path.exists(folder_path):
                continue
            parent_folder = os.path.dirname(folder_path)
            # Retrieve the paths of the folder contents.
            contents = os.walk(folder_path)
            if os.path.isfile(folder_path):
                zip_file.write(folder_path)

            try:
                for root, folders, files in contents:
                    # Include all subfolders, including empty ones.
                    for folder_name in folders:
                        absolute_path = os.path.join(root, folder_name)
                        relative_path = absolute_path.replace(parent_folder + '\\',
                                                              '')
                        logging.debug("Adding '%s' to archive." % absolute_path)
                        zip_file.write(absolute_path, relative_path)
                    for file_name in files:
                        absolute_path = os.path.join(root, file_name)
                        relative_path = absolute_path.replace(parent_folder + '\\',
                                                              '')
                        logging.debug("Adding '%s' to archive." % absolute_path)
                        zip_file.write(absolute_path, relative_path)
            except IOError as message:
                logging.critical(message)
                continue
            except OSError as message:
                logging.critical(message)
                continue
            except zipfile.BadZipfile as message:
                print("errr")
                logging.error(message)
                continue
        logging.debug("'%s' created successfully." % output_path)
    return output_path


def zipping_files(paths: list, output_path) -> str:
    backups_foleds = []
    with ZipFile('backup-mega.zip', 'w') as tmp_zip:
        for path_foled in paths:
            if path.exists(path_foled):
                backups_foleds.append(path_foled)

    return zip_folder(backups_foleds, output_path)
