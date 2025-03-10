# --------------------------------------------------------
# Swin Transformer
# Copyright (c) 2021 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ze Liu
# --------------------------------------------------------

import functools
import logging
import os

from termcolor import colored


@functools.lru_cache()
def create_logger(output_dir, name=""):
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # create formatter
    fmt = "[%(asctime)s %(name)s] (%(filename)s %(lineno)d): %(levelname)s %(message)s"
    color_fmt = colored("[%(asctime)s %(name)s]", "green") + colored("(%(filename)s %(lineno)d)", "yellow") + ": %(levelname)s %(message)s"

    # create file handlers
    file_handler = logging.FileHandler(os.path.join(output_dir, "log_file.txt"), mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(file_handler)

    return logger
