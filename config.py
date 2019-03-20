# Defaults for Job File
DEFAULT_CLIENT = "bareos-fd"
DEFAULT_JOB_DEFS = "DefaultJob"
DEFAULT_STORAGE = "S3_Object"

# File Writing Locations
JOB_FILE_LOCATION = "/etc/bareos/bareos-dir.d/job"
FILESET_FILE_LOCATION = "/etc/bareos/bareos-dir.d/fileset"
GIT_LOCATION = "/etc/bareos"

# Bareos Capabilities
COMPRESSION_OPTIONS = [
    "GZIP",
    "GZIP1",
    "GZIP2",
    "GZIP3",
    "GZIP4",
    "GZIP5",
    "GZIP6",
    "GZIP7",
    "GZIP8",
    "GZIP9",
    "LZO",
    "LZFAST",
    "LZ4",
    "LZ4HC",
]

