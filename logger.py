#!/usr/bin/env python3

import logging
import logging.handlers


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.SysLogHandler(address="/dev/log")
    handler.setFormatter(
        logging.Formatter(
            "brs_backup.%(funcName)s: [%(levelname)s] %(message)s"
        )
    )
    logger.addHandler(handler)

    return logger
