# -*- coding: utf-8 -*-
''' Module containing classes and methods for interaction with ODM's github repo

'''
import json
import base64
import sys
import os
import traceback

# Interface definition
class IGithubApi:

  def get_library_records(self):
    raise NotImplementedError

# Mock implementation
class TestGithubApi (IGithubApi):

  def __init__(self):

    return

  def get_library_records(self):

    pathToFile = os.path.join(os.path.dirname(__file__), "test/library.mrc")
    with open(pathToFile, 'rb') as f:
      return f.read()


# Real implementation
class RealGithubApi (IGithubApi):

  def __init__(self):

    return

  def get_library_records(self):

    pathToFile = os.path.join(os.path.dirname(__file__), '../../../../odm-library/records.mrc')
    with open(pathToFile, 'r') as f:
      return f.read()
