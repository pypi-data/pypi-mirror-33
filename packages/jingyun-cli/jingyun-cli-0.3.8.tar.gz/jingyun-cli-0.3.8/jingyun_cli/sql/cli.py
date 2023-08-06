#! /usr/bin/env python
# coding: utf-8

import os
import sys
from mysqldb_rich.db2 import TableDB
from jingyun_cli import logger
from jingyun_cli.util.cli_args import args_man
from jingyun_cli.util.help import error_and_exit
from jingyun_cli.util.env import get_environ
try:
    from .help import g_help
except ValueError:
    from help import g_help

__author__ = '鹛桑够'


def check_file_exist(file_path):
    if os.path.exists(file_path) is False:
        error_and_exit(g_help("file_lost", file_path))


def create_table(args):
    if args.conf_path is None:
        args.conf_path = get_environ("DB_CONF_PATH")
    t = TableDB(conf_path=args.conf_path)
    for item in args.files:
        logger.info(g_help("handle_file", item))
        check_file_exist(item)
        r = t.create_from_json_file(item)
    if args.directory is not None:
        t.create_from_dir(args.directory)


def op_table():
    commands_man = args_man.add_subparsers(title="Commands", description=None, metavar="COMMAND OPTIONS", dest="sub_cmd")
    create_man = commands_man.add_parser("create", help=g_help("create"))
    create_man.add_argument("-c", metavar="path", dest="conf_path", help=g_help("conf_path"))
    create_man.add_argument("-d", metavar="path", dest="directory", help=g_help("dir"))
    create_man.add_argument("-f", metavar="path", dest="files", help=g_help("file"), action="append", default=[],)

    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = args_man.parse_args()
    if args.sub_cmd == "create":
        create_table(args)


if __name__ == "__main__":
    sys.argv.extend(["create", "-f", "../../../GATCAPI/Table/Structure/gene.json"])
    op_table()
