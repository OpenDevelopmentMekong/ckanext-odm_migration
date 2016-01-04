#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import ODC contents
# This script imports Posts from the ODC wordpress site which have been
# previously exported as XML and stored on
# https://github.com/OpenDevelopmentMekong/odm-migration

import sys
import os
import io
import ckanapi
import lxml
import json
import uuid
import locale, datetime
from pymarc import MARCReader, marcxml
from lxml import etree
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data')))
import metadata
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
import data_utils
import ckanapi_utils
import script_utils
import traceback

try:
  sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'config')))
  import config
except ImportError as e:
  sys.exit(
      "Please make sure that you have renamed and initialized config.py.sample.py")

# Extending common config
config.dry = False
config.organization = 'cambodia-organization'
config.field_prefixes = {
  'en': [{'field': 'file_name_en', 'lang':'en', 'prefix': 'https://cambodia.opendevelopmentmekong.net/wp-content/blogs.dir/2/download/law/'}],
  'km': [{'field': 'file_name_kh', 'lang':'km', 'prefix': 'https://cambodia.opendevelopmentmekong.net/wp-content/blogs.dir/2/download/law/'}]
}
config.law_number_map = {
  'en': 'number_en',
  'km': 'number_kh'
}
config.supported_countries = ['kh','th','vi','la','mm']
config.supported_languages = ['en','km']
config.package_type = 'laws_record'
config.odm_spatial_range = 'kh'
config.supported_fields = [
  ('file_name_kh','File (Khmer)',False),#
  ('file_name_en','File (English)',False),
  ('adopted_date','Adopted Date',False),
  ('number_en','Number (English)',False),
  ('number_kh','Number (Khmer)',False),
  ('published_date','Publication date',False),
  ('published_under','Published under',False)
]
config.trace = str(uuid.uuid4())
config.taxonomy_tag_vocab='taxonomy'


data = data_utils.RealDataApi()
taxonomies = data.load_data_from_csv('data/taxonomy_map.csv')
laws_type_map = data.load_data_from_csv('data/laws_type_map.csv')
ckanapiutils = ckanapi_utils.RealCkanApi(config)

def _copy_resources_info(existing_metadata, metadata):

  metadata['resources'] = existing_metadata['resources']

  return metadata

def _set_title_translated(existing_metadata, metadata, lang):

  title_translated = {}
  if existing_metadata and 'title_translated' in existing_metadata:
    title_translated = existing_metadata['title_translated']

  if 'title' in metadata and metadata['title']:
    title_translated[lang] = metadata['title']
    metadata['title_translated'] = title_translated

  return metadata

def _set_notes_translated(existing_metadata, metadata, lang):

  notes_translated = {}
  if existing_metadata and 'notes_translated' in existing_metadata:
    notes_translated = existing_metadata['notes_translated']

  if 'notes' in metadata and metadata['notes']:
    notes_translated[lang] = metadata['notes']
    metadata['notes_translated'] = notes_translated

  return metadata

def _set_odm_laws_number(existing_metadata, metadata, lang):

  odm_laws_number = {}

  if existing_metadata and 'odm_document_number' in existing_metadata:
    odm_laws_number = existing_metadata['odm_document_number']

  law_number_key = config.law_number_map[lang]
  if law_number_key in metadata and metadata[law_number_key]:
    odm_laws_number[lang] = metadata[law_number_key]
    metadata['odm_document_number'] = odm_laws_number

  return metadata

def _set_odm_language(existing_metadata, metadata, lang):

  odm_language = []

  if existing_metadata and 'odm_language' in existing_metadata:
    filtered_list=filter(lambda x: x in config.supported_languages, existing_metadata['odm_language'])
    if filtered_list:
      odm_language = filtered_list

  odm_language.append(lang)
  metadata['odm_language'] = odm_language

  return metadata

def _set_odm_spatial_range(existing_metadata, metadata):

  odm_spatial_range = []

  if existing_metadata and 'odm_spatial_range' in existing_metadata:
    filtered_list=filter(lambda x: x in config.supported_countries, existing_metadata['odm_spatial_range'])
    if filtered_list:
      odm_spatial_range = filtered_list

  odm_spatial_range.append(config.odm_spatial_range)
  metadata['odm_spatial_range'] = odm_spatial_range
  
  return metadata

def _add_extras_urls_as_resources(dataset_metadata, field_prefixes, ckanapi_utils):

  for meta in elem.findall('wp:postmeta', root.nsmap):
    meta_key = meta.find('wp:meta_key', root.nsmap).text
    supported_fields = config.supported_fields
    if script_utils._is_key_in_fields(meta_key, supported_fields):
      meta_key_copy = meta_key
      meta_value = meta.find('wp:meta_value', root.nsmap).text
      if ((meta_value is not None) and (meta_value is not "")):

        field_key = meta_key
        field_value = meta_value

        if script_utils._is_valid_url(field_value):
          add_resource = True
          resource_format = 'html'
        else:
          for field_prefix in field_prefixes:
            if field_key == field_prefix['field']:
              field_value = field_prefix['prefix'] + field_value
              add_resource = True
              resource_format = script_utils._get_ext(field_value)

              if add_resource:

                try:

                  for resource in dataset_metadata['resources']:
                    if resource['name'] == dataset_metadata['title']:
                      continue

                  temp_file_path = script_utils._generate_temp_filename(script_utils._get_ext(field_value))
                  script_utils._download_file(field_value, temp_file_path)
                  resource_dict = script_utils._create_metadata_dictionary_for_upload(dataset_metadata['id'], "N/A", temp_file_path, dataset_metadata['title'], field_prefix['lang'].upper(), script_utils._get_ext(field_value),field_prefix['lang'])
                  created_resource = ckanapiutils.create_resource_with_file_upload(resource_dict)

                  if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

                except (UnicodeError):
                  traceback.print_exc()

def _set_taxonomy_from_category(dataset_metadata,elem):

  taxonomy_tags = ckanapiutils.get_all_tags_from_tag_vocabulary({'vocabulary_id': config.taxonomy_tag_vocab})

  dataset_metadata['taxonomy'] = []
  for category in elem.findall('category'):
    category_name = script_utils._prepare_string_for_ckan_tag_name(category.text)
    category_name = script_utils._str_capitalize_underscore_replaced_with_space(category_name)
    if category_name in taxonomies:
      mapped = taxonomies[category_name]
      for tag in mapped:
        tag_name = script_utils._prepare_string_for_ckan_tag_name(tag)
        tag_name = script_utils._str_capitalize_underscore_replaced_with_space(tag_name)
    else:
      tag_name = script_utils._prepare_string_for_ckan_tag_name(category_name)
      tag_name = script_utils._str_capitalize_underscore_replaced_with_space(category_name)

    if tag_name not in dataset_metadata['taxonomy']:
      if tag_name in taxonomy_tags:
        dataset_metadata['taxonomy'].append(tag_name)

  return dataset_metadata

def _set_document_type_from_category(dataset_metadata, elem):

  document_type = 'others'
  for category in elem.findall('category'):
    if category.text in laws_type_map:
      mapped = laws_type_map[category.text]
      for law_type in mapped:
        document_type = law_type

  if document_type:
    dataset_metadata['document_type'] = document_type

  return dataset_metadata

def _set_mandatory_metadata_fields_laws(dataset_metadata):

  dataset_metadata['odm_laws_status'] = 'unspecified'

  if 'adopted_date' in dataset_metadata:
    date_str = dataset_metadata['adopted_date'].split('||')[0]
    date_str.replace(","," ")
    if date_str.endswith(" "):
      date_str = date_str[0:-1]
    try:
      date = datetime.datetime.strptime(date_str, "%d %B %Y")
      dataset_metadata['odm_promulgation_date'] = date.strftime("%m/%d/%Y")
    except:
      print("unparseable date %s",date_str)

  return dataset_metadata

def _set_extras(dataset_metadata, root, elem):

  for meta in elem.findall('wp:postmeta', root.nsmap):
    meta_key = meta.find('wp:meta_key', root.nsmap).text
    supported_fields = config.supported_fields
    if script_utils._is_key_in_fields(meta_key, supported_fields):
      meta_key_copy = meta_key
      meta_value = meta.find('wp:meta_value', root.nsmap).text
      if ((meta_value is not None) and (meta_value is not "")):
        dataset_metadata[meta_key] = meta_value

  return dataset_metadata

def _map_xml_item_to_ckan_dataset_dict(root, elem):

  try:
    organization = config.organization
    orga = ckanapiutils.get_organization_id_from_name(organization)
  except ckanapi.NotFound:
    print("Organization " + organization + " not found, please check config")

  dataset_metadata = {}
  dataset_metadata['type'] = config.package_type

  dataset_metadata['maintainer'] = config.IMPORTER_NAME
  dataset_metadata['maintainer_email'] = config.IMPORTER_EMAIL

  dataset_metadata['owner_org'] = orga['id']
  dataset_metadata['title'] = elem.find('title').text
  dataset_metadata['name'] = elem.find('wp:post_name', root.nsmap).text
  dataset_metadata['name'] = script_utils._prepare_string_for_ckan_name(dataset_metadata['name'])
  dataset_metadata['state'] = 'active'
  dataset_metadata['notes'] = elem.find('content:encoded', root.nsmap).text

  if (elem.find('wp:post_date', root.nsmap) is not None):
    dataset_metadata['odm_date_uploaded'] = elem.find('wp:post_date', root.nsmap).text

  return dataset_metadata

for lang in config.supported_languages:

  try:
    ontology_xml = data.load_odc_laws(lang)

    if (ontology_xml):

      try:

        context = etree.iterparse(io.BytesIO(ontology_xml), events=('end', ))
        context = iter(context)
        root = context.next()[1]
        counter = 0

        for event, elem in context:

          if event == "end" and elem.tag == "item":

            if (elem.find('wp:status', root.nsmap) is not None):
              status = elem.find('wp:status', root.nsmap).text

              if status == 'publish':

                if ((int(config.SKIP_N_DATASETS) > 0) and (counter < int(config.SKIP_N_DATASETS))):
                  counter += 1
                  continue

                dataset_metadata = _map_xml_item_to_ckan_dataset_dict(root, elem)
                dataset_metadata = _set_extras(dataset_metadata,root,elem)
                dataset_metadata = _set_taxonomy_from_category(dataset_metadata,elem)
                dataset_metadata = _set_document_type_from_category(dataset_metadata,elem)
                dataset_metadata = _set_mandatory_metadata_fields_laws(dataset_metadata)
                dataset_metadata = script_utils._set_mandatory_metadata_fields(dataset_metadata,config.trace)

                try:

                  existing_metadata = ckanapiutils.get_package_contents(dataset_metadata['name'])
                  dataset_metadata = _copy_resources_info(existing_metadata, dataset_metadata)

                  if config.SKIP_EXISTING:
                    if lang in existing_metadata['odm_language']:
                      print("Dataset skipped ", dataset_metadata['name'], lang, existing_metadata['odm_language'])
                      continue

                  dataset_metadata = _set_title_translated(existing_metadata, dataset_metadata, lang)
                  dataset_metadata = _set_notes_translated(existing_metadata, dataset_metadata, lang)
                  dataset_metadata = _set_odm_laws_number(existing_metadata, dataset_metadata, lang)
                  dataset_metadata = _set_odm_language(existing_metadata, dataset_metadata, lang)
                  dataset_metadata = _set_odm_spatial_range(existing_metadata,dataset_metadata)

                  if not config.dry:
                    dataset_metadata = ckanapiutils.update_package(dataset_metadata)
                    print("Dataset modified ", dataset_metadata['id'], dataset_metadata['title'], lang, existing_metadata['odm_language'])

                except (ckanapi.SearchError, ckanapi.NotFound) as e:

                  try:

                    dataset_metadata = _set_title_translated(None, dataset_metadata, lang)
                    dataset_metadata = _set_notes_translated(None, dataset_metadata, lang)
                    dataset_metadata = _set_odm_laws_number(None, dataset_metadata, lang)
                    dataset_metadata = _set_odm_language(None, dataset_metadata, lang)
                    dataset_metadata = _set_odm_spatial_range(None,dataset_metadata)

                    if not config.dry:
                      dataset_metadata = ckanapiutils.create_package(dataset_metadata)
                      print("Dataset created ", dataset_metadata['id'], dataset_metadata['title'])

                  except TypeError as e:

                    if (config.DEBUG):
                      print(e)

                if 'id' in dataset_metadata:
                  _add_extras_urls_as_resources(dataset_metadata, config.field_prefixes[lang], ckanapiutils)

            elem.clear()

        root.clear()

      except TypeError as e:
        if (config.DEBUG):
          traceback.print_exc()
      except etree.XMLSyntaxError as e:
        if (config.DEBUG):
          traceback.print_exc()

  except KeyError as e:
    print("Source file not available for lang %s", lang)
    if (config.DEBUG):
      traceback.print_exc()

  except IOError as e:
    if (config.DEBUG):
      traceback.print_exc()

  print("COMPLETED import_odc_laws")
