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
import json
import ckan.model as model

ckanapiutils = ckanapi_utils.LocalCkanApi()

config = dict()

def _get_all_dataset_ids():

  s = """SELECT p.id as id FROM package p
      """

  res_ids = model.Session.execute(s).fetchall()
  res_pkgs = [pkg_id[0] for pkg_id in res_ids]
  return res_pkgs

def _is_khmer(value):
  try:
    value.decode(encoding='UTF-8',errors='strict')
    return False
  except:
    return True

def _copy_notes(dataset):

  if 'notes_translated' in dataset and type(dataset['notes_translated']) is dict:
    print('notes_translated already present ' + str(dataset['notes_translated']))
    return dataset

  value = dataset['notes']

  dataset['notes_translated'] = {
    'en': "",
    'km': "",
    'vi': "",
    'th': ""
  }

  lang = 'en'
  if _is_khmer(value):
    print('is khmer' + str(value))
    lang = 'km'

  dataset['notes_translated'][lang] = value

  return dataset

def _copy_title(dataset):

  if 'title_translated' in dataset and type(dataset['title_translated']) is dict:
    print('title_translated already present ' + str(dataset['title_translated']))
    return dataset

  value = dataset['title']

  dataset['title_translated'] = {
    'en': "",
    'km': "",
    'vi': "",
    'th': ""
  }

  lang = 'en'
  if _is_khmer(value):
    print('is khmer' + str(value))
    lang = 'km'

  dataset['title_translated'][lang] = value

  return dataset

def _convert_field_to_multilingual(field,dataset):

  if field in dataset:

    value = dataset[field]

    if type(value) is dict:
      print(str(field) + 'is already multilingual ' + str(value))
      return dataset

    dataset[field] = {
      'en': "",
      'km': "",
      'vi': "",
      'th': ""
    }

    lang = 'en'
    if _is_khmer(value):
      lang = 'km'

    dataset[field][lang] = value

  return dataset

class S6_migrate_to_multilingual(object):

  @classmethod
  def __init__(self):
    print("S6_migrate_to_multilingual init")

    config['dry'] = False

    return

  @classmethod
  def run(self):

    print("S6_migrate_to_multilingual run (DATASETS)")

    # True == 1
    # False == 0
    updated_datasets = []

    all_dataset_ids = _get_all_dataset_ids()

    for dataset_id in all_dataset_ids:
      dataset = ckanapiutils.get_package_contents(dataset_id)
      print('Converting '+ dataset['id'])

      if dataset['type'] == 'dataset':
        print('type dataset')
        dataset = _convert_field_to_multilingual('odm_access_and_use_constraints',dataset)
        dataset = _convert_field_to_multilingual('odm_accuracy',dataset)
        dataset = _convert_field_to_multilingual('odm_logical_consistency',dataset)
        dataset = _convert_field_to_multilingual('odm_completeness',dataset)
        dataset = _convert_field_to_multilingual('odm_metadata_reference_information',dataset)
        dataset = _convert_field_to_multilingual('odm_attributes',dataset)

      if dataset['type'] == 'library_record':
        print('type library_record')
        dataset = _convert_field_to_multilingual('odm_access_and_use_constraints',dataset)
        dataset = _convert_field_to_multilingual('marc21_246',dataset)
        dataset = _convert_field_to_multilingual('odm_contact',dataset)
        dataset = _convert_field_to_multilingual('marc21_260a',dataset)
        dataset = _convert_field_to_multilingual('marc21_260b',dataset)
        dataset = _convert_field_to_multilingual('marc21_300',dataset)
        dataset = _convert_field_to_multilingual('marc21_500',dataset)

      dataset = _copy_title(dataset)
      dataset = _copy_notes(dataset)

      if config['dry'] == False:
        dataset['odm_multilingual'] = 1
        ckanapiutils.update_package(dataset)
        updated_datasets.append(dataset['id'])

    return updated_datasets
