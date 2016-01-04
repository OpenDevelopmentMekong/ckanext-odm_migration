#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import from Geoserver
# This script imports all Layers from GeoServer using the import_from_geoserver function
# from the ODMImporter.

import sys
import os
import logging
import lxml
import io
import uuid
import ckanapi
import urllib2
from lxml import etree
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
import geoserver_utils
import ckanapi_utils
import script_utils

try:
  sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'config')))
  import config
except ImportError as e:
  sys.exit("Please make sure that you have renamed and initialized config.sample.py")

# Extending common config
config.ontology = '*'
config.organization = 'cambodia-organization'
config.package_type = 'dataset'
config.odm_spatial_range = 'kh'
config.taxonomy_tag_vocab='taxonomy'
config.trace = str(uuid.uuid4())

geoserver = geoserver_utils.RealGeoserverRestApi(config)
ckanapiutils = ckanapi_utils.RealCkanApi(config)

log = logging.getLogger(__name__)

def _map_geoserver_feature_to_ckan_dataset(feature_namespace,feature_name,feature_title,taxonomy_tags,config):

  # First, extract the information from the layer (Title, Abstract, Tags)
  params_dict = {}

  # Specify the package_type
  params_dict['type'] = config.package_type

  params_dict['maintainer'] = config.IMPORTER_NAME
  params_dict['maintainer_email'] = config.IMPORTER_EMAIL

  # The dataset id will be set when we find or create it
  params_dict['state'] = 'active'

  # Extract title (Mandatory)
  params_dict['title'] = feature_title

  # Extract name (Mandatory, lowcase and without characters except _-')
  params_dict['name'] = script_utils._prepare_string_for_ckan_name(feature_name)

  # Notes / Description / Abstract
  params_dict['notes'] = 'Imported Geoserver Layer: '+params_dict['title'] + '.'

  params_dict['taxonomy'] = []
  category_name = script_utils._prepare_string_for_ckan_tag_name(feature_namespace)
  category_name =  script_utils._str_capitalize_underscore_replaced_with_space(category_name)
  if (config.DEBUG):
    print(category_name)
  if (category_name in taxonomy_tags):
    params_dict['taxonomy'].append(category_name)

  return params_dict

def _set_extras_from_layer_to_ckan_dataset_dict(dataset_metadata,config):

  # Spatial range
  spatial_range = []
  spatial_range.append(config.odm_spatial_range)
  dataset_metadata['odm_spatial_range'] = spatial_range

  # Add Language
  language = []
  if dataset_metadata['name'].endswith('_kh'):
    language.append('km')
  else:
    language.append('en')
  dataset_metadata['odm_language'] = language

  return dataset_metadata

def _map_geoserver_feature_to_ckan_dataset(feature_namespace,feature_name,feature_title,taxonomy_tags,config):

  # First, extract the information from the layer (Title, Abstract, Tags)
  params_dict = {}

  # Specify the package_type
  params_dict['type'] = config.package_type

  params_dict['maintainer'] = config.IMPORTER_NAME
  params_dict['maintainer_email'] = config.IMPORTER_EMAIL

  # The dataset id will be set when we find or create it
  params_dict['state'] = 'active'

  # Extract title (Mandatory)
  params_dict['title'] = feature_title

  # Extract name (Mandatory, lowcase and without characters except _-')
  params_dict['name'] = script_utils._prepare_string_for_ckan_name(feature_name)

  # Notes / Description / Abstract
  params_dict['notes'] = 'Imported Geoserver Layer: '+params_dict['title'] + '.'

  params_dict['taxonomy'] = []
  category_name = script_utils._prepare_string_for_ckan_tag_name(feature_namespace)
  category_name =  script_utils._str_capitalize_underscore_replaced_with_space(category_name)
  if (category_name in taxonomy_tags):
    params_dict['taxonomy'].append(category_name)

  return params_dict

try:
  organization = config.organization
  orga = ckanapiutils.get_organization_id_from_name(organization)
except ckanapi.NotFound:
  sys.exit("Organization " + organization + " not found, please check config");

taxonomy_tags = ckanapiutils.get_all_tags_from_tag_vocabulary({'vocabulary_id':config.taxonomy_tag_vocab})

# Use geoserver_utils to get a dictionary with the layers
response_dict = geoserver.get_layers()

context = etree.iterparse(io.BytesIO(response_dict), events=('end', ))
context = iter(context)

root = context.next()[1]
counter = 0

for event, elem in context:

  if event == "end" and elem.tag == "layer":

    if (elem.find('name') is not None):
      name = elem.find('name').text
      feature_type_layer = geoserver.get_feature_type_layer(name)
      feature_type_layer_context = etree.iterparse(io.BytesIO(feature_type_layer), events=('end', ))
      feature_type_layer_context = iter(feature_type_layer_context)

      # call get_feature_type_info to get the feature type information of the layer
      feature_type_info = geoserver.get_feature_type_info(feature_type_layer_context)
      feature_type_info_context = etree.iterparse(io.BytesIO(feature_type_info), events=('end', ))
      feature_type_info_context = iter(feature_type_info_context)
      for event, info in feature_type_info_context:
        if event == "end" and info.tag == "title":
            title = info.text

      feature_namespace = name.split(":")[0]
      feature_name = name.split(":")[1]
      feature_title = title

    try:

      # Create dictionary with data to create/update datasets on CKAN
      dataset_metadata = _map_geoserver_feature_to_ckan_dataset(feature_namespace,feature_name,feature_title,taxonomy_tags,config)
      dataset_metadata = _set_extras_from_layer_to_ckan_dataset_dict(dataset_metadata,config)
      dataset_metadata = script_utils._set_mandatory_metadata_fields(dataset_metadata,config.trace)

      # Get id of organization from its name and add it to dataset_metadata
      dataset_metadata['id'] = ''
      dataset_metadata['owner_org'] = orga['id']

      if (config.DEBUG):
        print(dataset_metadata)

      try:

        response = ckanapiutils.get_package_contents(dataset_metadata['name'].lower())

        if config.SKIP_EXISTING:
          print("Dataset skipped ",dataset_metadata['id'],dataset_metadata['name'])
          continue

        # Lets modify it
        modified_dataset = ckanapiutils.update_package(dataset_metadata)
        dataset_metadata['id'] = modified_dataset['id']

        print("Dataset modified ",modified_dataset['id'],modified_dataset['title'])

      except (ckanapi.SearchError,ckanapi.NotFound) as e1:

        # Lets create it
        created_dataset = ckanapiutils.create_package(dataset_metadata)
        dataset_metadata['id'] = created_dataset['id']

        print("Dataset created ",created_dataset['id'],created_dataset['title'])

      ol_url = script_utils._generate_wms_download_url(geoserver.geoserver_url,feature_namespace,feature_name,'application/openlayers')
      resource_dict = script_utils._create_metadata_dictionary_for_resource(dataset_metadata['id'],ol_url,dataset_metadata['title'],'Data representation [Open Layers]','html')
      created_resource = ckanapiutils.create_resource(resource_dict)

      ol_url = script_utils._generate_wms_download_url(geoserver.geoserver_url,feature_namespace,feature_name,'application/vnd.google-earth.kml')
      resource_dict = script_utils._create_metadata_dictionary_for_resource(dataset_metadata['id'],ol_url,dataset_metadata['title'],'Data representation KML]','kml')
      created_resource = ckanapiutils.create_resource(resource_dict)

      try:

        temp_file_path = script_utils._generate_temp_filename('geojson')
        geojson_url = script_utils._generate_ows_download_url(geoserver.geoserver_url,feature_namespace,feature_name,'json')
        geojson_file = geoserver.download_file(geojson_url,temp_file_path)

        resource_dict = script_utils._create_metadata_dictionary_for_upload(dataset_metadata['id'],geojson_url,temp_file_path,dataset_metadata['title'],'Data representation [Geojson]','geojson',dataset_metadata['odm_language'][0])
        ckanapiutils.create_resource_with_file_upload(resource_dict)
        if os.path.exists(temp_file_path):
          os.remove(temp_file_path)

      except (urllib2.HTTPError, ValueError) as e3:
        if (config.DEBUG):
          traceback.print_exc()

      try:

        temp_file_path = script_utils._generate_temp_filename('csv')
        csv_url = script_utils._generate_ows_download_url(geoserver.geoserver_url,feature_namespace,feature_name,'csv')
        csv_file = geoserver.download_file(csv_url,temp_file_path)

        resource_dict = script_utils._create_metadata_dictionary_for_upload(dataset_metadata['id'],csv_file,temp_file_path,dataset_metadata['title'],'Data representation [CSV]','csv',dataset_metadata['odm_language'][0])
        ckanapiutils.create_resource_with_file_upload(resource_dict)
        if os.path.exists(temp_file_path):
          os.remove(temp_file_path)

      except (urllib2.HTTPError, ValueError) as e3:
        if (config.DEBUG):
          traceback.print_exc()

      file_formats = [
        {'mime':'image/png','ext':'png'},
        {'mime':'application/pdf','ext':'pdf'}
      ]

      for file_format in file_formats:

        try:

          temp_file_path = script_utils._generate_temp_filename(file_format['ext'])

          file_url = script_utils._generate_wms_download_url(geoserver.geoserver_url,feature_namespace,feature_name,file_format['mime'])
          file_contents = geoserver.download_file(file_url,temp_file_path)

          resource_dict = script_utils._create_metadata_dictionary_for_upload(dataset_metadata['id'],file_url,temp_file_path,dataset_metadata['title'],"Data representation ["+file_format['ext']+"]",file_format['ext'],dataset_metadata['odm_language'][0])
          ckanapiutils.create_resource_with_file_upload(resource_dict)
          if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        except (urllib2.HTTPError, ValueError) as e3:
          if (config.DEBUG):
            traceback.print_exc()

    except ckanapi.NotFound:
      if (config.DEBUG):
        traceback.print_exc()

    except (KeyError,ValueError) as e2:
      if (config.DEBUG):
        traceback.print_exc()
      continue

print("COMPLETED import_from_geoserver")
