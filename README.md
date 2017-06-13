# dinghy

![dinghy logo](dinghy.png)

CLI tool for RunDeck backup and restore.

[![CircleCI](https://circleci.com/gh/jonatanblue/dinghy/tree/master.svg?style=shield)](https://circleci.com/gh/jonatanblue/dinghy/tree/master)

**NOTE:** This project is still in beta. Please proceed with caution.

# How to use

## Install

    pip3 install -r requirements

## Run

### Backup

Backup everything and save to a `.tar.gz` file with the current date and time. This will result in the file `/opt/rundeck-backup-2017-06-09--12-41-42.tar.gz` being created, where the timestamp is the time when the script started running.

    ./dinghy.py backup --dest /opt

Backup only database and storage, to the file `/opt/rundeck-backup-partial-2017-06-09--12-46-09.tar.gz` being created. `-partial-` indicates that only some directories were backed up.

    ./dinghy.py --dirs=/var/lib/rundeck/data,/var/lib/rundeck/var/storage backup --dest /opt/

### Restore

Restore all directories into their absolute paths on the host machine. If any file already exists, the restore **should** refuse to do anything and exit with an error and show the offending file.

    ./dinghy.py restore --file /opt/rundeck-backup-2017-55-09--08-06-19.tar.gz

Restore only the directory `/var/lib/rundeck/data`.

    ./dinghy.py --dirs=/var/lib/rundeck/data restore --file /opt/rundeck-backup-2017-55-09--08-06-19.tar.gz



# Test

    python3 -m unittest discover

# Contribute

Contributions are welcome. If you spot any bugs, then please submit an issue with the steps to reproduce it. You can also create issues for general questions, or if you have a suggestion for a new feature.

For bug fixes and new features, make sure you have added tests that cover the use cases before submitting your PR.

# Similar tools

* The [official docs](http://rundeck.org/2.6.11/administration/backup-and-recovery.html) describe two options: either manually copy all data, using a combination of tools, or export an archive file from the web. The latter can take several hours, and does not include all files you may need.
* [ersiko/rundeck-backup](https://github.com/ersiko/rundeck-backup) last commit 31 Mar 2013. There's a [blog post](https://blog.tomas.cat/en/2013/03/27/tool-manage-rundeck-backups/) describing how to use it.

# Acknowledgements

Thanks to [nvtkaszpir](https://github.com/nvtkaszpir) for initial feedback and suggestions.
