#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Delete law records
This script deletes all records with type = laws_record
'''

import sys
import os
import ckanapi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
import ckanapi_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data')))
import metadata
import traceback

ckanapiutils = ckanapi_utils.LocalCkanApi()

config = dict()

class S5_delete_all_laws(object):

  @classmethod
  def __init__(self):
    print("S5_delete_all_laws init")

    config['dry'] = False
    config['state'] = 'active'

    return

  @classmethod
  def run(self):

    print("S5_delete_all_laws run")

    try:

      params = {
        'fq': '+type:laws_record',
        'rows': 1000
      }

      orga_datasets = {}
      search_result = ckanapiutils.search_packages(params)
      datasets = search_result['results']

      for dataset in datasets:
        if dataset['owner_org'] not in orga_datasets.keys():
          orga_datasets[dataset['owner_org']] = []
        orga_datasets[dataset['owner_org']].append(dataset['id'])

      if config['dry'] == False:
        for orga_id in orga_datasets.keys():
          params = {'datasets':orga_datasets[orga_id],'org_id':orga_id}
          ckanapiutils.delete_packages_list(params)

    except ckanapi.NotFound:
      traceback.print_exc()

    return {
      'dry': config['dry'],
      'deleted' :orga_datasets
    }
