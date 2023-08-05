#! /usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
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


def environ_format():
    arg_man.add_argument("-i", "-I", "--input", dest="input", help=g_help("conf_file"), metavar="conf_file",
                         action="append", default=[])
    arg_man.add_argument("inputs", metavar="conf_file", nargs="*", help=g_help("conf_file"))
    arg_man.add_argument("-m", "--mode", dest="mode", help=g_help("mode"), type=int, choices=[1, 2], default=1)

    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = arg_man.parse_args()
    files = args.input
    files.extend(args.inputs)
    for item in files:
        print("format %s" % item)
        rewrite_conf(item, args.mode)
        print("format %s success\n" % item)

if __name__ == "__main__":
    sys.argv.extend(["../key/mns.conf", "-i", "../key/mns.conf"])
    environ_format()
