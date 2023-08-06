#! /usr/bin/env python
# coding: utf-8

import sys
from functools import partial
from jingyun_cli.util.help import help_value

__author__ = '鹛桑够'


output_help = {"en": "the output of file, default is work dir.", "cn": "下载后的文件保存的目录，默认保存到当前工作目录"}
oss_file_help = {"en": "the name of oss file", "cn": "oss 文件的文件名"}
oss_dir_help = {"en": "the oss directory of the oss file", "cn": "要下载的oss文件所在的oss目录"}
endpoint_help = {"en": "oss server endpoint, for example http://jy-softs.oss-cn-beijing.aliyuncs.com",
                 "cn": "服务器端点,例如http://jy-softs.oss-cn-beijing.aliyuncs.com"}

name_help = {"en": "", "cn": "下载后保存的文件名，仅在下载文件只有一个时有效，超过一个下载文件将忽略该参数"}
exist_help = {"en": "", "cn": "文件%s已存在将不执行下载操作"}
error_help = {"en": "", "cn": "下载文件%s未执行成功"}
download_help = {"en": "", "cn": "下载文件 %s 到 %s"}

help_keys = filter(lambda x: x.endswith("_help"), locals().keys())
help_dict = dict()
for key in help_keys:
    help_dict[key[:-5]] = locals()[key]


g_help = partial(help_value, help_dict)


def error_and_exit(msg, error_code=1):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    sys.exit(error_code)