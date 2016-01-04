#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Status imported library records
# This script goes through the list of library records exported from NGL and
# checks whether they are present in a CKAN instance

# NOTE: This script has to be run within a virtual environment!!!
# Do not forget to set the correct API Key while initialising RealCkanApi
# . /usr/lib/ckan/default/bin/activate

import sys
import os
import ckanapi
import uuid
from pymarc import MARCReader,marcxml
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
import data_utils
import ckanapi_utils
import ngl_utils
import script_utils
import library_utils

try:
  sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'config')))
  import config
except ImportError as e:
  sys.exit("Please make sure that you have renamed and initialized config.sample.py")

# Extending common config
config.organization = 'cambodia-organization'
config.package_type = 'library_record'
config.output_file = './report.json'
config.odm_spatial_range= 'Cambodia'
config.trace = str(uuid.uuid4())

data = data_utils.RealDataApi()
ckanapiutils = ckanapi_utils.RealCkanApi(config)
nglutils = ngl_utils.RealNGLApi(config)

records = data.load_marc21_records()
records_found = []
records_not_found = []

try:
  organization = config.organization
  orga = ckanapiutils.get_organization_id_from_name(organization)
except ckanapi.NotFound:
  sys.exit("Organization " + organization + " not found, please check config");

reader = MARCReader(records)
counter = 0
for record in reader:

  if ((int(config.SKIP_N_DATASETS) > 0) and (counter < int(config.SKIP_N_DATASETS))):
    counter += 1
    continue

  dataset_metadata = library_utils._map_record_to_ckan_dataset_dict(record,config)

  if (dataset_metadata is None) or (dataset_metadata["name"] == ''):
    print("Dataset does not have any title or ISBN, unique name cannot be checked")
    continue

  dataset_metadata = library_utils._set_extras_from_record_to_ckan_dataset_dict(dataset_metadata,record,config)
  dataset_metadata = script_utils._set_mandatory_metadata_fields(dataset_metadata,config.trace)

  dataset_metadata['owner_org'] = orga['id']

  try:

    response = ckanapiutils.get_package_contents(dataset_metadata['name'])

    if config.SKIP_EXISTING:
      print("Dataset skipped ",dataset_metadata['name'])
      continue

    records_found.append(response)
    print("Dataset found ",response['id'],response['title'])

  except (ckanapi.SearchError,ckanapi.NotFound) as e:

    try:

      records_not_found.append(dataset_metadata)
      print("Dataset not found ",dataset_metadata['id'],dataset_metadata['title'])

    except (ckan.lib.search.common.SearchIndexError) as e:
      continue

print(str(len(records_found)) + " records found" )
print(str(len(records_not_found)) + " records missing" )
f1 = open(config.output_file, 'w+')
f1.write(str(records_not_found))

print("COMPLETED status_imported_library_records")
