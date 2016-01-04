#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Changes the type of the datasets in a certain group

# NOTE: This script has to be run within a virtual environment!!!
# Do not forget to set the correct API Key while initialising RealCkanApi
# . /usr/lib/ckan/default/bin/activate

# NOTE!!!! Changing the dataset type programatically is currently avoided,
# tweaking the code indicated on https://github.com/ckan/ckan/commit/7224d4c76e2f74af52ae9af6798cf3ed1c6034c9
# allows to run this function.

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
config.dry = True
config.type = 'library_record'
config.organization = 'cambodia-organization'
config.state = 'active'
config.limit = 500
config.field_filter = {'odm_contact':'OD Mekong Importer','odm_contact_email':'info@opendevmekong.net'}

ckanapiutils = ckanapi_utils.RealCkanApi(config)

try:

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
        supported_fields = metadata_utils.odc_fields + metadata_utils.metadata_fields + metadata_utils.library_fields
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

        try:

          dataset_metadata = ckanapiutils.get_package_contents(dataset['id'])

          if dataset_metadata['type'] == config.type:
            print("Dataset skipped ",dataset_metadata['name'])
            continue

          if config.dry == False:
            dataset_metadata['type'] = config.type
            dataset_metadata = ckanapiutils.update_package(dataset_metadata)
            print("Dataset modified ",dataset_metadata['id'],dataset_metadata['title'],dataset_metadata['type'])

          counter = counter + 1

        except (ckanapi.SearchError,ckanapi.NotFound) as e:

          if (config.DEBUG):
            print(e)

except ckanapi.NotFound as e:

  if (config.DEBUG):
    print(e)

print("COMPLETED change_dataset_type_in_group")
