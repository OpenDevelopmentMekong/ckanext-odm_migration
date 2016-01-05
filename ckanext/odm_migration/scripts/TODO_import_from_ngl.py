#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import from NextGenLib
# This script imports all records from a MARC21 formatted file (available on github)
# as datasets.

# NOTE: This script has to be run within a virtual environment!!!
# Do not forget to set the correct API Key while initialising RealCkanApi
# . /usr/lib/ckan/default/bin/activate

import sys
import os
import urllib2
import urllib
import ckanapi
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
import github_utils
import ckanapi_utils
import ngl_utils
import library_utils
import data_utils
import script_utils
from pymarc import MARCReader,marcxml

try:
  sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'config')))
  import config
except ImportError as e:
  sys.exit("Please make sure that you have renamed and initialized config.sample.py")

# Extending common config
config.organization = 'cambodia-organization'
config.package_type = 'library_record'
config.odm_spatial_range = 'Cambodia'
config.trace = str(uuid.uuid4())

data = data_utils.RealDataApi()
ckanapiutils = ckanapi_utils.RealCkanApi(config)
nglutils = ngl_utils.RealNGLApi(config)

records = data.load_marc21_records()

try:
  organization = config.organization
  orga = ckanapiutils.get_organization_id_from_name(organization)
except ckanapi.NotFound:
  sys.exit("Organization " + organization + " not found, please check config")

reader = MARCReader(records)
counter = 0
for record in reader:

  if ((int(config.SKIP_N_DATASETS) > 0) and (counter < int(config.SKIP_N_DATASETS))):
    counter += 1
    continue

  dataset_metadata = library_utils._map_record_to_ckan_dataset_dict(record,config)

  if (dataset_metadata is None) or (dataset_metadata["name"] == ''):
    print("Dataset does not have any title or ISBN, unique name cannot be generated")
    continue

  dataset_metadata = library_utils._set_extras_from_record_to_ckan_dataset_dict(dataset_metadata,record,config)
  dataset_metadata = script_utils._set_mandatory_metadata_fields(dataset_metadata,config.trace)

  dataset_metadata['owner_org'] = orga['id']

  try:

    response = ckanapiutils.get_package_contents(dataset_metadata['name'])

    if config.SKIP_EXISTING:
      print("Dataset skipped ",dataset_metadata['name'])
      continue

    modified_dataset = ckanapiutils.update_package(dataset_metadata)
    dataset_metadata['id'] = modified_dataset['id']
    print("Dataset modified ",modified_dataset['id'],modified_dataset['title'])

  except (ckanapi.SearchError,ckanapi.NotFound) as e:

    try:
      created_dataset = ckanapiutils.create_package(dataset_metadata)
      dataset_metadata['id'] = created_dataset['id']
      print("Dataset created ",created_dataset['id'],created_dataset['title'])

    except (ckan.lib.search.common.SearchIndexError) as e:
      continue

  try:

    temp_file_path = script_utils._generate_temp_filename('xml')

    with open(temp_file_path, 'w') as fw:
      xml = marcxml.record_to_xml(record)
      fw.write(xml)
      fw.close()

    resource_dict = script_utils._create_metadata_dictionary_for_upload(dataset_metadata['id'],"N/A",temp_file_path,dataset_metadata['title'],'Alternative representation [MARCXML]','xml',None)
    ckanapiutils.create_resource_with_file_upload(resource_dict)
    if os.path.exists(temp_file_path):
      os.remove(temp_file_path)

  except (ValueError, OSError) as e:
    if (config.DEBUG):
      traceback.print_exc()

  try:

    temp_file_path = script_utils._generate_temp_filename('json')

    with open(temp_file_path, 'w') as fw:
      json = record.as_json()
      fw.write(json)
      fw.close()

    resource_dict = script_utils._create_metadata_dictionary_for_upload(dataset_metadata['id'],"N/A",temp_file_path,dataset_metadata['title'],'Alternative representation [JSON]','json',None)
    ckanapiutils.create_resource_with_file_upload(resource_dict)
    if os.path.exists(temp_file_path):
      os.remove(temp_file_path)

  except (ValueError, OSError) as e:
    if (config.DEBUG):
      traceback.print_exc()

  try:

    temp_file_path = script_utils._generate_temp_filename('mrc')

    with open(temp_file_path, 'wb') as fw:
      json = record.as_marc()
      fw.write(json)
      fw.close()

    resource_dict = script_utils._create_metadata_dictionary_for_upload(dataset_metadata['id'],"N/A",temp_file_path,dataset_metadata['title'],'Record [MARC21]','mrc',None)
    ckanapiutils.create_resource_with_file_upload(resource_dict)
    if os.path.exists(temp_file_path):
      os.remove(temp_file_path)

  except (ValueError, OSError) as e:
    if (config.DEBUG):
      traceback.print_exc()

  if record.get_fields('856'):
    for f in record.get_fields('856'):

      if f['u'] is not None:
        resource_url = f['u']

        try:

          urllib.urlopen(resource_url)
          resource_dict = script_utils._create_metadata_dictionary_for_resource(dataset_metadata['id'],resource_url,dataset_metadata['title'],'Extra material [Link]','html',None)
          created_resource = ckanapiutils.create_resource(resource_dict)

        except (UnicodeError):
          if (config.DEBUG):
            traceback.print_exc()

        except (IOError, AttributeError) as e:

          try:

            temp_file_path = script_utils._generate_temp_filename('pdf')
            nglutils.download_file(resource_url,temp_file_path)
            resource_dict = script_utils._create_metadata_dictionary_for_upload(dataset_metadata['id'],"N/A",temp_file_path,dataset_metadata['title'],'Extra material [PDF]','pdf',None)
            ckanapiutils.create_resource_with_file_upload(resource_dict)
            if os.path.exists(temp_file_path):
              os.remove(temp_file_path)

          except (ValueError, OSError, TypeError) as e:
            if (config.DEBUG):
              traceback.print_exc()

print("COMPLETED import_marc21_library_records")
