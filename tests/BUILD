load("@pipdeps//:requirements.bzl", "requirement")

py_test(
    name="test_util",
    srcs=["test_util.py"],
    deps=[
        "//:config",
        "//:util",
        requirement("gitdb2"),
        requirement("smmap2"),
        requirement("GitPython"),
        requirement("mysql-connector-python"),
    ],
)
