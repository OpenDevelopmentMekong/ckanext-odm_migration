#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Delete datasets in group
# This script deletes all the datasets assigned to a group.

# NOTE: This script has to be run within a virtual environment!!!
# Do not forget to set the correct API Key while initialising RealCkanApi
# . /usr/lib/ckan/default/bin/activate

import sys
import os
import ckanapi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
import ckanapi_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data')))
import metadata

try:
  sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'config')))
  import config
except ImportError as e:
  sys.exit("Please make sure that you have renamed and initialized config.py.sample.py")

# Extending common config
config.dry = False
config.organization = 'cambodia-organization'
config.group = 'dataset'
config.state = 'active'
config.limit = 500
config.field_filter = None

ckanapiutils = ckanapi_utils.RealCkanApi(config)

try:

  orga_datasets = {}
  datasets = []
  counter = 0
  state_filter = config.state or None
  field_filter = config.field_filter or None
  if config.organization:
    params = {'id':config.organization}
    datasets = ckanapiutils.get_packages_in_organization(params)
  elif config.group:
    params = {'id':config.group,'limit':config.limit}
    datasets = ckanapiutils.get_packages_in_group(params)

  for dataset in datasets:
    if counter < int(config.limit):

      filter_matching = True
      if field_filter is not None:
        matching_extras = []
        supported_fields = metadata.odc_fields + metadata.metadata_fields + metadata.library_fields
        for field_key in field_filter.keys():
          if field_key in dataset and dataset[field_key] == field_filter[field_key]:
            if field_key not in matching_extras:
              matching_extras.append(field_key)

        if len(matching_extras) != len(field_filter.keys()):
          filter_matching = False

      state_matching = True
      if state_filter is not None and dataset['state'] != state_filter:
        state_matching = False

      if state_matching and filter_matching:
        if dataset['owner_org'] not in orga_datasets.keys():
          orga_datasets[dataset['owner_org']] = []
        orga_datasets[dataset['owner_org']].append(dataset['id'])
        counter = counter + 1

  if (config.DEBUG):
    print(orga_datasets)

  if config.dry == False:
    for orga_id in orga_datasets.keys():
      params = {'datasets':orga_datasets[orga_id],'org_id':orga_id}
      ckanapiutils.delete_packages_list(params)

except ckanapi.NotFound:

  print 'Group ' + config.group + ' not found'

print("COMPLETED delete_datasets_in_group")
