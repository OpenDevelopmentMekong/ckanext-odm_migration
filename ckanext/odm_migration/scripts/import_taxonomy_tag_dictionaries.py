#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import Taxonomy tag dictionaries
# Pulls the taxonomy from https://github.com/OpenDevelopmentMekong/odm-localization and stores
# as tag dictionaries.

import sys
import os
import ckanapi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
import geoserver_utils
import ckanapi_utils
import taxonomy_utils
import script_utils

try:
  sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'config')))
  import config
except ImportError as e:
  sys.exit("Please make sure that you have renamed and initialized config.sample.py")

# extending common config
config.taxonomy_tag_vocab='taxonomy'

taxonomyutils = taxonomy_utils.RealTaxonomyApi()
ckanapiutils = ckanapi_utils.RealCkanApi(config)

def _add_taxonomy_tag(taxonomy_tag_vocabulary,tag_name):

  tag_name = script_utils._prepare_string_for_ckan_tag_name(tag_name)

  tag = {'name': tag_name}

  # Avoid duplicates
  tag_exists = False
  for existing_tag in taxonomy_tag_vocabulary['tags']:
    if ( existing_tag['name'] == tag_name):
      tag_exists = True
      break;

  if (tag_exists == False):
    taxonomy_tag_vocabulary['tags'].append(dict(tag))

def _inspect_json_create_tags(inspected_dict,taxonomy_tag_vocabulary):
  print(inspected_dict)
  if 'children' in inspected_dict.keys():

      # Has children
      for child in inspected_dict['children']:

        _add_taxonomy_tag(taxonomy_tag_vocabulary,child['name'])

        # Iterate deeper
        _inspect_json_create_tags(child,taxonomy_tag_vocabulary)

  else:

    _add_taxonomy_tag(taxonomy_tag_vocabulary,inspected_dict['name'])

taxonomy_dict = taxonomyutils.get_taxonomy_for_locale('en')

try:

  # Create tag_vocabulary for taxonomy , it can happen that it has already been created
  taxonomy_tag_vocabulary = ckanapiutils.show_tag_vocabulary({'id': config.taxonomy_tag_vocab})

  # if found, reset tags in vocabulary
  taxonomy_tag_vocabulary['tags'] = list()

except ckanapi.NotFound:

  # Create tag_vocabulary for taxonomy , it can happen that it has already been created
  params_create = dict({'name':config.taxonomy_tag_vocab,'tags': list()})
  taxonomy_tag_vocabulary = ckanapiutils.create_tag_vocabulary(params_create)

# Loop through the json structure recursively and add tags to the vocabulary
_inspect_json_create_tags(taxonomy_dict,taxonomy_tag_vocabulary)

ckanapiutils.update_tag_vocabulary(taxonomy_tag_vocabulary)
print("COMPLETED import_taxonomy_tag_dictionaries " + str(len(taxonomy_tag_vocabulary['tags'])) + ' taxonomy tags imported in taxonomy vocabulary')
