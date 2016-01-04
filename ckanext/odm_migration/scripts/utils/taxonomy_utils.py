# -*- coding: utf-8 -*-
''' Module containing classes and methods for interaction with ODM's github repo

'''
import json
import base64
import sys
import os
import traceback
import urllib2
import urllib

# Interface definition
class ITaxonomyApi:

  def get_taxonomy_for_locale(self,locale):
    raise NotImplementedError

# Mock implementation
class TestTaxonomyApi (ITaxonomyApi):

  def __init__(self):

    return

  def get_taxonomy_for_locale(self,locale):

    return json.loads('{}')

# Real implementation
class RealTaxonomyApi (ITaxonomyApi):

  def __init__(self):

    return

  def get_taxonomy_for_locale(self,locale):

    request = urllib2.Request('https://raw.githubusercontent.com/OpenDevelopmentMekong/odm-taxonomy/master/taxonomy_'+locale+'.json')
    response = urllib2.urlopen(request)
    assert response.code == 200
    return json.loads(response.read())
