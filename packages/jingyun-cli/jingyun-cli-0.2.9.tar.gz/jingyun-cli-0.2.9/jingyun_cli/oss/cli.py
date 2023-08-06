#! /usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
from jingyun_cli import logger
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


def download_action(endpoint, oss_dir, oss_item, save_path, force=False):
    if os.path.exists(save_path) is True and force is False:
        logger.warning(g_help("exist", oss_item))
        return 0
    logger.info(g_help("download", oss_item, save_path))
    url = get_download_url(endpoint, oss_dir, oss_item)
    cmd = ["curl", "-o", save_path, url]
    e_code = os.system(" ".join(cmd))
    return e_code


def multi_download():
    arg_man.add_argument("-d", "--oss-dir", dest="oss_dir", help=g_help("oss_dir"), metavar="", default="")
    arg_man.add_argument("-e", "--endpoint", dest="endpoint", help=g_help("endpoint"), metavar="",
                         default=default_endpoint)
    arg_man.add_argument("-n", "--name", dest="name", metavar="filename", help=g_help("name"))
    arg_man.add_argument("-f", "--force", action="store_true", help=g_help("force"), default=False)
    arg_man.add_argument("files", metavar="oss_file", nargs="*", help=g_help("oss_file"))
    add_output()
    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = arg_man.parse_args()
    f_inputs = args.files
    out_dir = args.output
    if out_dir is None:
        out_dir = "."
    if len(f_inputs) == 1:
        name = args.name if args.name is not None else f_inputs[0]
        save_path = os.path.join(out_dir, name)
        e_code = download_action(args.endpoint, args.oss_dir, f_inputs[0], save_path, force=args.force)
        if e_code != 0:
            error_and_exit(g_help("error", f_inputs[0]))
    else:
        for item in f_inputs:
            save_path = os.path.join(out_dir, item)
            e_code = download_action(args.endpoint, args.oss_dir, item, save_path, force=args.force)
            if e_code != 0:
                error_and_exit(g_help("error", item))

if __name__ == "__main__":
    sys.argv.extend(["-d", "shell", "nonkey.sh", "deploy_api.sh", "-n", "a.sh", "-f"])
    multi_download()
