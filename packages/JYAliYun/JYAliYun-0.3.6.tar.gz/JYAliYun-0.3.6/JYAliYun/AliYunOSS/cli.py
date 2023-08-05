#! /usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
from JYAliYun.util.print_helper import print_table
from JYAliYun.AliYunOSS import OSSBucket

__author__ = '鹛桑够'

env_oss_conf = "OSS_CONF_PATH"


def receive_conf_path(conf_path):
    if conf_path is None:
        conf_path = os.environ.get(env_oss_conf)
        if conf_path is None:
            sys.stderr.write("Please use -c or --conf-path set oss configure path\n")
            sys.exit(1)
    return conf_path


def oss_head():
    arg_man = argparse.ArgumentParser()
    arg_man.add_argument("-c", "--conf-path", dest="conf_path", help="oss configure file path", metavar="")
    arg_man.add_argument("-b", "--bucket-name", dest="bucket_name", help="oss bucket name", metavar="")
    arg_man.add_argument("-o", "-O", "--object", dest="object", help="oss object path", action="append", metavar="",
                         default=[])
    arg_man.add_argument("objects", metavar="object", nargs="*", help="oss object path")
    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = arg_man.parse_args()
    conf_path = receive_conf_path(args.conf_path)
    o_objects = args.object
    o_objects.extend(args.objects)
    kwargs = dict(conf_path=conf_path)
    if args.bucket_name is not None:
        kwargs["bucket_name"] = args.bucket_name
    bucket_man = OSSBucket(**kwargs)
    exit_code = 0
    for o_item in set(o_objects):
        print("-" * 20 + "start head %s" % o_item + "-" * 20)
        resp = bucket_man.head_object(o_item)
        if resp.status_code != 200:
            print("head fail! oss server return %s" % resp.status_code)
            exit_code += 1
            continue
        t = [["Header Key", "Header Value"], ["------------", "------------"]]
        for k, v in resp.headers.items():
            t.append([k, v])
        print_table(t)
    sys.exit(exit_code)


def list_object():
    arg_man = argparse.ArgumentParser()
    arg_man.add_argument("-c", "--conf-path", dest="conf_path", help="oss configure file path", metavar="")
    arg_man.add_argument("-b", "--bucket-name", dest="bucket_name", help="oss bucket name", metavar="")
    arg_man.add_argument("-d", "--oss_dir", dest="oss_dir", help="oss dir", action="append", metavar="",
                         default=[])
    arg_man.add_argument("-r", "--region", dest="region", help="bucket region", metavar="")
    arg_man.add_argument("oss_dirs", metavar="oss_dirs", nargs="*", help="oss dir")
    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = arg_man.parse_args()
    conf_path = receive_conf_path(args.conf_path)
    oss_dirs = args.oss_dir
    oss_dirs.extend(args.oss_dirs)
    kwargs = dict(conf_path=conf_path)
    if args.bucket_name is not None:
        kwargs["bucket_name"] = args.bucket_name
    if args.region is not None:
        kwargs["region"] = args.region
    bucket_man = OSSBucket(**kwargs)
    exit_code = 0
    for d_item in set(oss_dirs):
        resp = bucket_man.list_all_object(d_item)
        if resp.status_code != 200:
            sys.stderr.write("list fail! oss server return %s\n" % resp.status_code)
            exit_code += 1
            break
        keys = resp.data["keys"]
        for item in keys:
            print(item["key"][len(d_item):])
    sys.exit(exit_code)


def get_objects():
    arg_man = argparse.ArgumentParser()
    arg_man.add_argument("-c", "--conf-path", dest="conf_path", help="oss configure file path", metavar="")
    arg_man.add_argument("-b", "--bucket-name", dest="bucket_name", help="oss bucket name", metavar="")
    arg_man.add_argument("-d", "--oss_dir", dest="oss_dir", help="oss dir", metavar="")
    arg_man.add_argument("-r", "--region", dest="region", help="bucket region", metavar="")
    arg_man.add_argument("-o", "--output", dest="output", metavar="", help="output dir", default=".")
    arg_man.add_argument("-v", "--verbose", dest="verbose", help="print all message", action="store_true",
                         default=False)
    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = arg_man.parse_args()
    conf_path = receive_conf_path(args.conf_path)
    oss_dir = args.oss_dir
    out_dir = args.output
    kwargs = dict(conf_path=conf_path)
    if args.bucket_name is not None:
        kwargs["bucket_name"] = args.bucket_name
    if args.region is not None:
        kwargs["region"] = args.region
    bucket_man = OSSBucket(**kwargs)
    exit_code = 0
    resp = bucket_man.list_all_object(oss_dir, delimiter="/")
    if resp.status_code != 200:
        sys.stderr.write("list fail! oss server return %s\n" % resp.status_code)
        sys.exit(1)
    keys = resp.data["keys"]
    for item in keys:
        key = item["key"]
        if key.endswith("/") is True:
            continue
        save_name = key[len(oss_dir):]
        save_path = os.path.join(out_dir, save_name)
        if args.verbose is True:
            print("download %s to %s" % (save_name, save_path))
        response = bucket_man.get_object(key, save_path)
        if response.status_code != 200:
            sys.stderr.write(response.status_code)
            sys.exit(1)
        print(save_path)

    sys.exit(exit_code)

if __name__ == "__main__":
    sys.argv.extend(["-b", "geneac", "-r", "beijing", "-d", "geneacdata/bson/"])
    get_objects()