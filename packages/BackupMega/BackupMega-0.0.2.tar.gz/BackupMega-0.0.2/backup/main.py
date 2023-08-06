import os
import subprocess
from datetime import datetime
from os.path import join
from pathlib import Path
from backup.build_files import zipping_files


def backup():
    home_folder = str(Path.home())
    path_conf = join(home_folder, "backup-mega.txt")
    now = datetime.now()
    output_file = '/tmp/backup/{}-{}-{}_{}:{}:{}.zip'.format(
        now.date().day,
        now.date().month,
        now.date().year,
        now.time().hour,
        now.time().minute,
        now.time().second,
    )
    with open(path_conf) as f:
        conf_file = f.read()

    zipping_files(conf_file.split('\n'), output_file)
    save_backup_in_storage(backup_path=output_file)


def save_backup_in_storage(storage: str='mega', backup_path: str='/tmp/backup/'):
    if storage == 'mega':
        return save_in_mega(backup_path)
    return None


def save_in_mega(backup_path: str):
    if not mega_is_exists_backup_folder():
        os.system('megamkdir /Root/Backup')
    os.system('megacopy --local {} --remote {}'.format(os.path.dirname(backup_path), '/Root/Backup'))


def mega_is_exists_backup_folder() -> bool:
    folders = subprocess.Popen("megals /Root".split(), stdout=subprocess.PIPE)
    return b'/Root\n/Root/Backup\n' in folders.communicate(timeout=20)
