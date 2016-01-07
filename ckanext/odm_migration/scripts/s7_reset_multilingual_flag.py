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
import ckan.model as model

ckanapiutils = ckanapi_utils.LocalCkanApi()

config = dict()

def _get_all_dataset_ids():

  s = """SELECT p.id as id FROM package p
      """

  res_ids = model.Session.execute(s).fetchall()
  res_pkgs = [pkg_id[0] for pkg_id in res_ids]
  return res_pkgs

class S7_reset_multilingual_flag(object):

  @classmethod
  def __init__(self):
    print("S7_reset_multilingual_flag init")

    config['dry'] = False

    return

  @classmethod
  def run(self):

    print("S7_reset_multilingual_flag run")

    # True == 1
    # False == 0

    updated_datasets =  []

    all_dataset_ids = _get_all_dataset_ids()

    for dataset_id in all_dataset_ids:
      dataset = ckanapiutils.get_package_contents(dataset_id)
      print(dataset)
      if config['dry'] == False:
        dataset['odm_multilingual'] = 0
        ckanapiutils.update_package(dataset)
        updated_datasets.append(dataset['id'])

    return updated_datasets
