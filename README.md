# brs_backup

brs_backup is a utility to allow for easy adding and removing of user and group home directory backups from Bareos.

## Commands

brs_backup supports the following commands:  
    **add**     - Add user home directories to backups  
    **gadd**    - Add a group directory to backups  
    **gremove** - Remove a group directory from backups  
    **remove**  - Remove a user home directories from backups  

The '--help' flag is available with all commands to further explain their usage.

## Files

### config.py

Configuration setting for brs_backup

### secrets.py

Should contain the following variables:  
**bconsole_password**   - password to bconsole  
**sql_username**        - username to core CHPC MySQL server 
**sql_password**        - password to core CHPC MySQL server  

### logger.py

Provides logging facilities to log to syslog.

### util.py

Provides file writing and database reading utilities.

### main.py

Provides the CLI interface for brs_backup.
