load("@pipdeps//:requirements.bzl", "requirement")
load("@subpar//:subpar.bzl", "par_binary")

py_runtime(
    name = "python-3.6.3",
    files = [],
    interpreter_path = "/uufs/chpc.utah.edu/sys/installdir/python/3.6.3/bin/python",
    # Required for pip imports.
    visibility = ["//visibility:public"],
)

par_binary(
    name = "brs_backup",
    srcs = ["main.py"],
    main = "main.py",
    deps = [
        ":util",
        ":logger",
        ":config",
        requirement("Click"),
    ],
    default_python_version = "PY3",
)    

py_library(
    name = "util",
    srcs = ["util.py"],
    deps = [
        ":config",
        ":secrets",
        ":logger",
        ":bareos",
        requirement("mysql-connector-python"),
        requirement("GitPython"),
        requirement("gitdb2"),
        requirement("smmap2"),
    ],
    data = [
        ":templates", 
    ],
    visibility = ["//visibility:public"],
)

py_library(
    name = "config",
    srcs = ["config.py"],
    visibility = ["//visibility:public"],
)

py_library(
    name = "secrets",
    srcs = ["secrets.py"],
    visibility = ["//visibility:public"],
)

py_library(
    name = "logger",
    srcs = ["logger.py"],
    visibility = ["//visibility:public"],
)

py_library(
    name = "bareos",
    srcs = glob(["bareos/**/*.py"]),
    visibility = ["//visibility:public"],
)
