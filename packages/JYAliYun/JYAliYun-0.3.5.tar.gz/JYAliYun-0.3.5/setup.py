#! /usr/bin/env python
# coding: utf-8

#  __author__ = 'ZhouHeng'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys

if sys.version_info <= (2, 7):
    sys.stderr.write("ERROR: jingyun aliyun python sdk requires Python Version 2.7 or above.\n")
    sys.stderr.write("Your Python Version is %s.%s.%s.\n" % sys.version_info[:3])
    sys.exit(1)

name = "JYAliYun"
version = "0.3.5"
url = "https://github.com/meisanggou/AliYun"
license = "MIT"
author = "meisanggou"
short_description = "Aliyun Service Library"
long_description = """JYAliYun provides interfaces to AliYun Service."""
keywords = "JYAliYun"
install_requires = ["requests", "lxml", "six"]

setup(name=name,
      version=version,
      author=author,
      author_email="zhouheng@gene.ac",
      url=url,
      packages=["JYAliYun", "JYAliYun/util", "JYAliYun/AliYunMNS", "JYAliYun/Tools", "JYAliYun/AliYunOSS",
                "JYAliYun/AliYunRAM"],
      license=license,
      description=short_description,
      long_description=long_description,
      keywords=keywords,
      install_requires=install_requires,

      entry_points='''[console_scripts]
            oss-head=JYAliYun.AliYunOSS.cli:oss_head
            head-oss=JYAliYun.AliYunOSS.cli:oss_head
            oss-list=JYAliYun.AliYunOSS.cli:list_object
            oss-get=JYAliYun.AliYunOSS.cli:get_objects
            list-oss=JYAliYun.AliYunOSS.cli:list_object
            publish-message=JYAliYun.AliYunMNS.cli:publish_message
            mns-pm=JYAliYun.AliYunMNS.cli:publish_message
      '''
      )
