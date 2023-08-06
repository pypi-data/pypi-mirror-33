#! /usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
import re
try:
    from .help import g_help, error_and_exit
except ValueError:
    from help import g_help, error_and_exit

__author__ = '鹛桑够'


arg_man = argparse.ArgumentParser()


def rewrite_conf(file_path, mode):
    if os.path.exists(file_path) is False:
        msg = g_help("file_not_exist", file_path)
        error_and_exit(msg)
    try:
        with open(file_path) as rf:
            c = rf.read()
    except IOError:
        error_and_exit(g_help("read_error", file_path))
        return
    if mode == 2:
        n_c = c % os.environ
    else:
        n_c = c.format(**os.environ)
    with open(file_path, "w") as w:
        w.write(n_c)


def list_files(directory, prefix, end, re_filter):
    files = os.listdir(directory)
    # 按照前缀筛选
    if prefix is not None:
        files = filter(lambda x: x.startswith(prefix), files)
    # 按照后缀筛选
    if end is not None:
        files = filter(lambda x: x.endswith(end), files)
    # 按照正则筛选
    if re_filter is not None:
        files = filter(lambda x: re.match(re_filter, x), files)

    # 获取全路径
    files = map(lambda x: os.path.join(directory, x), files)
    # 去除目录
    files = filter(lambda x: os.path.isfile(x), files)
    return files


def environ_format():
    arg_man.add_argument("-d", "--directory", dest="directory", help=g_help("directory"), metavar="directory")
    arg_man.add_argument("-p", "--prefix", dest="prefix", help=g_help("prefix"), metavar="prefix")
    arg_man.add_argument("-e", "--end", dest="end", help=g_help("end"), metavar="end")
    arg_man.add_argument("-f", "--filter", dest="filter", help=g_help("filter"), metavar="filter", default=r"\S*")
    arg_man.add_argument("-i", "-I", "--input", dest="input", help=g_help("conf_file"), metavar="conf_file",
                         action="append", default=[])
    arg_man.add_argument("inputs", metavar="conf_file", nargs="*", help=g_help("conf_file"))
    arg_man.add_argument("-m", "--mode", dest="mode", help=g_help("mode"), type=int, choices=[1, 2], default=1)

    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = arg_man.parse_args()
    files = args.input
    files.extend(args.inputs)
    if args.directory is not None:
        files.extend(list_files(args.directory, args.prefix, args.end, args.filter))
    for item in files:
        print("format %s" % item)
        rewrite_conf(item, args.mode)
        print("format %s success\n" % item)

if __name__ == "__main__":
    sys.argv.extend(["-d", "/data/Web2/conf", "-p", "m", "-e", ".conf", "-f", r"\S+?_\S+"])
    environ_format()
