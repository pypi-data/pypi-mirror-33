#! /usr/bin/env python
# coding: utf-8

import sys
from functools import partial
from jingyun_cli.util.help import help_value

__author__ = '鹛桑够'

conf_file_help = {"en": "the path of conf file", "cn": "配置文件的路径"}
file_not_exist_help = {"en": "file %s not exist", "cn": "文件%s不存在"}
read_error_help = {"en": "read file %s error", "cn": "读取文件%s失败"}
write_error_help = {"en": "rewrite file %s error", "cn": "重写文件%s失败"}
mode_help = {"en": "1 use str.format(os.environ),2 use str %% os.environ",
             "cn": "1代表使用str.format(os.environ)，2代表使用str %% os.environ"}


help_keys = filter(lambda x: x.endswith("_help"), locals().keys())
help_dict = dict()
for key in help_keys:
    help_dict[key[:-5]] = locals()[key]

g_help = partial(help_value, help_dict)


def error_and_exit(msg, error_code=1):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    sys.exit(error_code)
