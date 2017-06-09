# dinghy

![dinghy logo](dinghy.png)

CLI tool for RunDeck backup and restore.

**NOTE:** This project is **NOT** ready for production use.

# How to use

## Install

    pip3 install -r requirements

## Run

### Backup

Backup everything and save to a `.zip` file with the current date and time. This will result in the file `/opt/rundeck-backup-2017-06-09--12-41-42.zip` being created, where the timestamp is the time when the script started running.

    ./dinghy.py backup --dest /opt

Backup only database and storage, to the file `/opt/rundeck-backup-partial-2017-06-09--12-46-09.zip` being created. `-partial-` indicates that only some directories were backed up.

    ./dinghy.py --dirs=/var/lib/rundeck/data,/var/lib/rundeck/var/storage backup --dest /opt/

### Restore

Restore all directories into their absolute paths on the host machine. If any file already exists, the restore **should** refuse to do anything and exit with an error and show the offending file.

    ./dinghy.py restore --file /opt/rundeck-backup-2017-55-09--08-06-19.zip

Restore only the directory `/var/lib/rundeck/data`.

    ./dinghy.py --dirs=/var/lib/rundeck/data restore --file /opt/rundeck-backup-2017-55-09--08-06-19.zip



# Test

    python3 -m unittest discover
