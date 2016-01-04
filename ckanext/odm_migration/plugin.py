from logging import getLogger

import ckan.plugins as p

log = getLogger(__name__)

class OdmMigrationPlugin(p.SingletonPlugin):
    '''ODM Migration plugin.'''

    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer, inherit=True)

    def after_map(self, map):
        map.connect('odm_migration', '/migration',
            controller='ckanext.odm_migration.controller:MigrationController',
            action='run')
        return map

    def update_config(self, config):
        templates = 'templates'
        p.toolkit.add_template_directory(config, templates)
