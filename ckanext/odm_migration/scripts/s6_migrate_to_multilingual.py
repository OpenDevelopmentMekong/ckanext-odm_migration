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
import json
import ckan.model as model
import traceback
import ckan

ckanapiutils = ckanapi_utils.LocalCkanApi()

config = dict()

def _get_all_dataset_ids():

  s = """SELECT p.id as id FROM package p
      """

  res_ids = model.Session.execute(s).fetchall()
  res_pkgs = [pkg_id[0] for pkg_id in res_ids]
  return res_pkgs

# def _is_khmer(value):
#   print("checking if value is in khmer " + str(value))
#   try:
#     value.decode('ascii')
#   except UnicodeDecodeError:
#     return True
#   else:
#     return False

def _is_english(value):
  for c in set(['a', 'e', 'i', 'o', 'u']):
      if c in value:
        return True;
  return False;


def _copy_notes(dataset):

  if 'notes_translated' in dataset and type(dataset['notes_translated']) is dict:
    print('notes_translated already present ' + str(dataset['notes_translated']))
    return dataset

  if 'notes' not in dataset:
    return dataset

  value = dataset['notes']

  if not value:
    return dataset

  if isinstance(value, basestring):
    value = value.encode('utf-8')

  notes_dict = {
    'en': "",
    'km': "",
    'vi': "",
    'th': ""
  }

  lang = 'km'
  if _is_english(value):
    lang = 'en'

  notes_dict[lang] = value
  dataset['notes_translated'] = json.dumps(notes_dict)

  return dataset

def _copy_title(dataset):

  if 'title_translated' in dataset and type(dataset['title_translated']) is dict:
    print('title_translated already present ' + str(dataset['title_translated']))
    return dataset

  if 'title' not in dataset:
    return dataset

  value = dataset['title']

  if not value:
    return dataset

  if isinstance(value, basestring):
    value = value.encode('utf-8')

  title_dict = {
    'en': "",
    'km': "",
    'vi': "",
    'th': ""
  }

  lang = 'km'
  if _is_english(value):
    lang = 'en'

  title_dict[lang] = value
  dataset['title_translated'] = json.dumps(title_dict)

  return dataset

def _convert_field_to_multilingual(field,dataset):
  print("_convert_field_to_multilingual " + field)

  if field in dataset:

    value = dataset[field]

    if type(value) is dict:
      print(str(field) + " is already multilingual ")
      return dataset

    value = value.encode('utf-8')

    field_dict = {
      'en': "",
      'km': "",
      'vi': "",
      'th': ""
    }

    lang = 'km'
    if _is_english(value):
      lang = 'en'

    field_dict[lang] = value
    dataset[field] = json.dumps(field_dict)

  return dataset

def _convert_odm_spatial_range(dataset):

  if 'odm_spatial_range' in dataset:
    if type(dataset['odm_spatial_range']) is list:
      return dataset

    odm_spatial_range = []

    if dataset['odm_spatial_range'].lower().find('laos') > -1:
      odm_spatial_range.append('la')
    if dataset['odm_spatial_range'].lower().find('vietnam') > -1:
      odm_spatial_range.append('vn')
    if dataset['odm_spatial_range'].lower().find('thailand') > -1:
      odm_spatial_range.append('th')
    if dataset['odm_spatial_range'].lower().find('myanmar') > -1:
      odm_spatial_range.append('mm')
    if dataset['odm_spatial_range'].lower().find('cambodia') > -1:
      odm_spatial_range.append('kh')
    if dataset['odm_spatial_range'].lower().find('global') > -1:
      odm_spatial_range.append('global')
    if dataset['odm_spatial_range'].lower().find('asean') > -1:
      odm_spatial_range.append('asean')
    if dataset['odm_spatial_range'].lower().find('greater mekong subregion (gms)') > -1:
      odm_spatial_range.append('gms')
    if dataset['odm_spatial_range'].lower().find('lower mekong basin') > -1:
      odm_spatial_range.append('lmb')
    if dataset['odm_spatial_range'].lower().find('lower mekong countries') > -1:
      odm_spatial_range.append('lmc')

    dataset['odm_spatial_range'] = odm_spatial_range
    print("Setting odm_spatial_range " + str(odm_spatial_range))

  return dataset

def _convert_odm_language(dataset):

  if 'odm_language' in dataset:
    if type(dataset['odm_language']) is list:
      return dataset

    odm_language = []

    if dataset['odm_language'].lower().find('vi') > -1:
      odm_language.append('vi')
    if dataset['odm_language'].lower().find('vietnamese') > -1:
      odm_language.append('vi')
    if dataset['odm_language'].lower().find('en') > -1:
      odm_language.append('en')
    if dataset['odm_language'].lower().find('english') > -1:
      odm_language.append('en')
    if dataset['odm_language'].lower().find('lo') > -1:
      odm_language.append('lo')
    if dataset['odm_language'].lower().find('lao') > -1:
      odm_language.append('lo')
    if dataset['odm_language'].lower().find('th') > -1:
      odm_language.append('th')
    if dataset['odm_language'].lower().find('thai') > -1:
      odm_language.append('th')
    if dataset['odm_language'].lower().find('my') > -1:
      odm_language.append('my')
    if dataset['odm_language'].lower().find('burmese') > -1:
      odm_language.append('my')
    if dataset['odm_language'].lower().find('zh') > -1:
      odm_language.append('zh')
    if dataset['odm_language'].lower().find('chinese') > -1:
      odm_language.append('zh')
    if dataset['odm_language'].lower().find('fr') > -1:
      odm_language.append('fr')
    if dataset['odm_language'].lower().find('french') > -1:
      odm_language.append('fr')
    if dataset['odm_language'].lower().find('de') > -1:
      odm_language.append('de')
    if dataset['odm_language'].lower().find('german') > -1:
      odm_language.append('de')
    if dataset['odm_language'].lower().find('jp') > -1:
      odm_language.append('jp')
    if dataset['odm_language'].lower().find('japanese') > -1:
      odm_language.append('jp')
    if dataset['odm_language'].lower().find('ko') > -1:
      odm_language.append('ko')
    if dataset['odm_language'].lower().find('korean') > -1:
      odm_language.append('ko')
    if dataset['odm_language'].lower().find('other') > -1:
      odm_language.append('other')

    dataset['odm_language'] = odm_language
    print("Setting odm_language " + str(odm_language))

  return dataset

class S6_migrate_to_multilingual(object):

  @classmethod
  def __init__(self):
    print("S6_migrate_to_multilingual init")

    config['dry'] = False

    return

  @classmethod
  def run(self):
    print("S6_migrate_to_multilingual run")

    updated_datasets = []
    all_dataset_ids = _get_all_dataset_ids()
    for dataset_id in all_dataset_ids:
      dataset = ckanapiutils.get_package_contents(dataset_id)
      if 'odm_multilingual' not in dataset or ('odm_multilingual' in dataset and dataset['odm_multilingual'] == 0):
        print('Converting '+ dataset_id)

        try:

          if 'type' in dataset['type'] == 'dataset':
            print('type dataset')
            dataset = _convert_field_to_multilingual('odm_access_and_use_constraints',dataset)
            dataset = _convert_field_to_multilingual('odm_accuracy',dataset)
            dataset = _convert_field_to_multilingual('odm_contact',dataset)
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

          dataset = _convert_odm_spatial_range(dataset)
          dataset = _convert_odm_language(dataset)
          dataset = _copy_title(dataset)
          dataset = _copy_notes(dataset)

          if config['dry'] == False:
            dataset['odm_multilingual'] = 1
            ckanapiutils.update_package(dataset)
            updated_datasets.append(dataset['id'])

        except UnicodeDecodeError:
          traceback.print_exc()
        except ckan.logic.ValidationError:
          traceback.print_exc()
        except:
          traceback.print_exc()

      else:
        print("skipping dataset " + dataset_id)

    return updated_datasets
