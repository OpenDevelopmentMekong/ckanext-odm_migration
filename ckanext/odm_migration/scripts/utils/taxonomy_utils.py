# -*- coding: utf-8 -*-
''' Module containing classes and methods for interaction with ODM's github repo

'''

import requests

SOURCE_URL = 'https://raw.githubusercontent.com/OpenDevelopmentMekong/odm-taxonomy/master/2.2/taxonomy_%s.json'

# Interface definition
class ITaxonomyApi:
    def get_taxonomy_for_locale(self,locale):
        raise NotImplementedError

# Mock implementation
class TestTaxonomyApi (ITaxonomyApi):
    def get_taxonomy_for_locale(self,locale):
        return {}

# Real implementation
class RealTaxonomyApi (ITaxonomyApi):
    def get_taxonomy_for_locale(self,locale):
        return requests.get(SOURCE_URL % locale).json()
