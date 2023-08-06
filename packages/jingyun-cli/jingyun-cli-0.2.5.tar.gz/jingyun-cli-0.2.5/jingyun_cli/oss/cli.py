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


default_endpoint = "http://jy-softs.oss-cn-beijing.aliyuncs.com"
arg_man = argparse.ArgumentParser()


def add_output():
    arg_man.add_argument("-o", "--output", dest="output", help=g_help("output"), metavar="output")


def get_download_url(endpoint, oss_dir, oss_file):
    endpoint = endpoint.rstrip("/")
    oss_dir = oss_dir.strip("/")
    if len(oss_dir) > 0:
        url = "%s/%s/%s" % (endpoint, oss_dir, oss_file)
    else:
        url = "%s/%s" % (endpoint, oss_file)
    return url


def multi_download():
    arg_man.add_argument("-d", "--oss-dir", dest="oss_dir", help=g_help("oss_dir"), metavar="", default="")
    arg_man.add_argument("-e", "--endpoint", dest="endpoint", help=g_help("endpoint"), metavar="",
                         default=default_endpoint)
    arg_man.add_argument("-f", "--file", dest="file", help=g_help("oss_file"), action="append", metavar="oss_file",
                         default=[])
    arg_man.add_argument("files", metavar="oss_file", nargs="*", help=g_help("oss_file"))
    add_output()
    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = arg_man.parse_args()
    f_inputs = args.files
    f_inputs.extend(args.file)
    out_dir = args.output
    if out_dir is None:
        out_dir = "."
    for item in f_inputs:
        save_path = os.path.join(out_dir, item)
        url = get_download_url(args.endpoint, args.oss_dir, item)
        cmd = ["curl", "-o", save_path, url]
        e_code = os.system(" ".join(cmd))

if __name__ == "__main__":
    sys.argv.extend(["-d", "shell", "nonkey.sh", "a.sh"])
    multi_download()
