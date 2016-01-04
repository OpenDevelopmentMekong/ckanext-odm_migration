import ckan.plugins as p
import sys
import os
import ckan.lib.base as base
from ckan.lib.base import BaseController, config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'scripts')))
import s1_insert_initial_odm_data
import s2_import_taxonomy_tag_dictionaries
import s3_import_taxonomy_term_translations
import s4_import_odc_laws
import s10_migrate_to_multilingual
import ckan.lib.helpers as h

c = base.c
request = base.request
_ = base._

class MigrationController(BaseController):

    def run(self):

      if ('insert_initial_odm_data' in request.params):

        script = s1_insert_initial_odm_data.S1_insert_intial_odm_data()
        c.script_results = script.run()

        return p.toolkit.render('ckanext/migration/result.html')

      elif ('import_taxonomy_tag_dictionaries' in request.params):

        script = s2_import_taxonomy_tag_dictionaries.S2_import_taxonomy_tag_dictionaries()
        c.script_results = script.run()

        return p.toolkit.render('ckanext/migration/result.html')

      elif ('import_taxonomy_term_translations' in request.params):

        script = s3_import_taxonomy_term_translations.S3_import_taxonomy_term_translations()
        c.script_results = script.run()

        return p.toolkit.render('ckanext/migration/result.html')

      elif ('import_odc_laws' in request.params):

        script = s4_import_odc_laws.S4_import_odc_laws()
        c.script_results = script.run()

        return p.toolkit.render('ckanext/migration/result.html')

      elif ('migrate_to_arrays' in request.params):

        script = s10_migrate_to_multilingual.S10_migrate_to_multilingual()
        c.script_results = script.run()

        return p.toolkit.render('ckanext/migration/result.html')

      else:

        return p.toolkit.render('ckanext/migration/index.html')
