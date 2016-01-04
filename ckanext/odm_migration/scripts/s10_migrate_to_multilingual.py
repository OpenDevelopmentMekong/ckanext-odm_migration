#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Migrate to multilingual
'''

import sys
import os
import ckanapi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
import ckanapi_utils
import traceback

ckanapiutils = ckanapi_utils.LocalCkanApi()

config = dict()

class S10_migrate_to_multilingual(object):

  @classmethod
  def __init__(self):
    print("S10_migrate_to_multilingual init")

    return

  @classmethod
  def run(self):

    print("S10_migrate_to_multilingual run")

    params = {}
    return ckanapiutils.get_package_list(params)
