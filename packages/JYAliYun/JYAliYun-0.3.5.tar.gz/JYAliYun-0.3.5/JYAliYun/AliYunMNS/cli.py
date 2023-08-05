#! /usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
from JYAliYun.AliYunMNS.AliMNSServer import MNSServerManager

__author__ = '鹛桑够'

env_mns_conf = "MNS_CONF_PATH"


def receive_conf_path(conf_path):
    if conf_path is None:
        conf_path = os.environ.get(env_mns_conf)
        if conf_path is None:
            sys.stderr.write("Please use -c or --conf-path set mns configure path\n")
            sys.exit(1)
    return conf_path


def publish_message():
    description = "publish message to ali mns server"
    arg_man = argparse.ArgumentParser(description=description)
    arg_man.add_argument("-c", "--conf-path", dest="conf_path", help="mns configure file path", metavar="")
    arg_man.add_argument("-t", "--topic-name", dest="topic_name", help="topic name", metavar="")
    arg_man.add_argument("-m", metavar=("message-tag", "message-body"), dest="message", nargs=2,
                         help="input message-tag and message-body", required=True)
    arg_man.format_help()
    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = arg_man.parse_args()

    conf_path = receive_conf_path(args.conf_path)

    mns_server = MNSServerManager(conf_path=conf_path)
    mns_topic = mns_server.get_topic(args.topic_name)

    if mns_topic.topic_name is None:
        sys.stderr.write("please top_name use -t or --topic-name\n")
        sys.exit(1)
    r = mns_topic.publish_message(args.message[1], message_tag=args.message[0], is_thread=False)
    if r.status_code == 404:
        sys.stderr.write("topic-name %s not exist, please check!\n" % mns_topic.topic_name)
        sys.exit(2)
    if r.status_code / 100 == 2:
        print("success")
        sys.exit(0)
    sys.stderr.write("not known error [%s]\n" % r.status_code)
    sys.exit(3)


if __name__ == "__main__":
    publish_message()