#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Import taxonomy term translations
This script imports multi-lingual taxonomy from https://github.com/OpenDevelopmentMekong/odm-localization
and stores term translations.
'''

from utils import ckanapi_utils
from utils import taxonomy_utils
from utils import script_utils
from ckan.lib import jobs
ckanapiutils = ckanapi_utils.LocalCkanApi()
taxonomyutils = taxonomy_utils.RealTaxonomyApi()

config = dict()

class S3_import_taxonomy_term_translations(object):

  config = dict()

  def __init__(self):
    self.supported_langs=['en','km','th','vi','lo', 'my']

  def run(self):

    print("S3_import_taxonomy_term_translations run")

    added_term_translations = []

    # Obtain JSON File from Github containing the different translations
    locales = self.supported_langs
    term_lists = {}
    terms_to_import = []

    # Generate term lists for each one of the supported locales
    for locale in locales:

      # init list
      term_lists[locale] = []

      try:

        # Obtain the translation_dict from github
        translation_dict = taxonomyutils.get_taxonomy_for_locale(locale)

        # Call utility function
        script_utils._inspect_json_dict_fill_list(translation_dict, term_lists[locale])

      except Exception as e:
        if config.DEBUG:
          print("File for locale " + locale +" not found. Check your config and make sure that the file is available on the odm-localization repository.")

    # Now loop through the term_lists
    for locale_origin in locales:

      # Set counter
      other_locales = list(locales)
      other_locales.remove(locale_origin)

      # Now loop through the terms of the particular locale
      for term_position, term in enumerate(term_lists[locale_origin]):

        # For each term, we add a term translation of each of the other languages
        for locale_destination in other_locales:
          try:
            orig_term = term_lists[locale_origin][term_position]
            dest_term = term_lists[locale_destination][term_position]

            if orig_term != dest_term:

              # Add term translation locale_origin -> locale_destination
              params1 = {'term':script_utils._prepare_string_for_ckan_tag_name(orig_term),'term_translation':dest_term,'lang_code':locale_destination}
              terms_to_import.append(dict(params1))

              print('Translating ' + params1['term'].encode("utf-8") + ' ('+ locale_origin + ') as ' + params1['term_translation'].encode("utf-8") + ' (' +  locale_destination + ')')

              # Add term translation locale_origin -> locale_destination
              params2 = {'term':script_utils._prepare_string_for_ckan_tag_name(dest_term),'term_translation':orig_term,'lang_code':locale_origin}
              terms_to_import.append(dict(params2))

              print('Translating ' + params2['term'].encode("utf-8") + ' ('+ locale_destination + ') as ' + params2['term_translation'].encode("utf-8") + ' (' +  locale_origin + ')')

          except IndexError:
            break

    count = 0
    if len(terms_to_import) > 0:
      result = ckanapiutils.add_term_translation_many(dict({'data':terms_to_import}))
      count = result["success"]

    return "COMPLETED import_taxonomy_term_translations " + str(count) + " terms imported successfully."

def translate(timeout=180):
    script = S3_import_taxonomy_term_translations()
    job = jobs.enqueue(script.run, args=[], timeout=timeout)
    job_id = job.id
    message = "Job has been assigned!!"
    return {'job_id':job_id, 'message':message, 'timeout':timeout}
