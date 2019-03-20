# brs_backup

brs_backup is a utility to allow for easy adding and removing of user and group home directory backups from Bareos.

## Commands

brs_backup supports the following commands:  
    **uadd**     - Add user home directories to backups  
    **add**      - Add a directory to backups  
    **remove**   - Remove a directory from backups  
    **uremove**  - Remove a user home directories from backups  

The '--help' flag is available with all commands to further explain their usage.

## Files

### config.py

Configuration setting for brs_backup

### secrets.py

Should contain the following variables:  

### logger.py

Provides logging facilities to log to syslog.

### util.py

Provides file writing and database reading utilities.

### main.py

Provides the CLI interface for brs_backup.

## Build
To build an executable "binary", I used Bazel (https://bazel.build). Inside of the root directory, run `bazel build :brs_backup`. The generated binary is 'bazel-bin/brs_backup.par'.

On the CHPC, an existing Bazel binary exists in '/uufs/chpc.utah.edu/common/home/u0407846/bin/bazel'.
