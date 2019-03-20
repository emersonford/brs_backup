# Adding support for Pip.
git_repository(
    name = "io_bazel_rules_python",
    remote = "https://github.com/bazelbuild/rules_python.git",
    commit = "7e5adb05b7aa4cba64a6dd1138f817670888b220",
)

load("@io_bazel_rules_python//python:pip.bzl", "pip_repositories")
pip_repositories()

load("@io_bazel_rules_python//python:pip.bzl", "pip_import")
pip_import(
   name = "pipdeps",
   requirements = "//:requirements.txt",
)

load("@pipdeps//:requirements.bzl", "pip_install")
pip_install()

# Adding support for .par files.
git_repository(
    name = "subpar",
    remote = "https://github.com/google/subpar",
    tag = "1.0.0",
)
