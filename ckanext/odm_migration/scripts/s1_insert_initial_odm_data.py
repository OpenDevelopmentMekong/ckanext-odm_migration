#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Insert initial ODM Data
This script initialises the CKAN Instance with a list of organizations, groups and users:
organizations (OD Mekong Cambodia, OD Mekong Laos, OD Mekong Thailand, OD Mekong Vietnam, OD Mekong Myanmar)
Groups (Cambodia, Laos, Thailand, Vietnam, Myanmar)
Users (odmcambodia, odmlaos, odmthailand, odmvietnam, odmmyanmar)
'''

import sys
import os
import ckanapi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
import ckanapi_utils
import traceback

ckanapiutils = ckanapi_utils.LocalCkanApi()

config = dict()

class S1_insert_intial_odm_data(object):

  @classmethod
  def __init__(self):
    print("S1_insert_intial_odm_data init")

    config['odm_admins_pass'] = 'odmadmin'

    return

  @classmethod
  def run(self):

    print("S1_insert_intial_odm_data run")

    result = dict({
      'users': [],
      'roles': [],
      'orgas': [],
      'groups': [],
      'errors': []
    })

    # Add Users
    for user in [{'name':'odmmekong','email':'mekong@opendevelopmentmekong.net','pass':config['odm_admins_pass'],'desc':'OD Mekong Mekong admin'},
                  {'name':'odmcambodia','email':'cambodia@opendevelopmentmekong.net','pass':config['odm_admins_pass'],'desc':'OD Mekong Cambodia admin'},
                  {'name':'odmlaos','email':'laos@opendevelopmentmekong.net','pass':config['odm_admins_pass'],'desc':'OD Mekong Laos admin'},
                  {'name':'odmthailand','email':'thailand@opendevelopmentmekong.net','pass':config['odm_admins_pass'],'desc':'OD Mekong Thailand admin'},
                  {'name':'odmvietnam','email':'vietnam@opendevelopmentmekong.net','pass':config['odm_admins_pass'],'desc':'OD Mekong Vietnam admin'},
                  {'name':'odmmyanmar','email':'myanmar@opendevelopmentmekong.net','pass':config['odm_admins_pass'],'desc':'OD Mekong Myanmar admin'}]:

      try:
        added_user = ckanapiutils.add_user(user['name'],user['email'],user['pass'],user['desc'])
        result['users'].append(added_user)
      except ckanapi.ValidationError as e:
        traceback.print_exc()
        result['errors'].append(e)

    # Add organizations
    for organization in [{'name':'mekong-organization','title':'Open Development Mekong','desc':'OD Mekong regional organization'},
                          {'name':'cambodia-organization','title':'Open Development Cambodia','desc':'Cambodia-based organizations and partners'},
                          {'name':'laos-organization','title':'Open Development Laos','desc':'Laos-based organizations and partners'},
                          {'name':'thailand-organization','title':'Open Development Thailand','desc':'Thailand-based organizations and partners'},
                          {'name':'vietnam-organization','title':'Open Development Vietnam','desc':'Vietnam-based organizations and partners'},
                          {'name':'myanmar-organization','title':'Open Development Myanmar','desc':'Myanmar-based organizations and partners'}]:

      try:
        added_orga = ckanapiutils.add_organization(organization['name'],organization['title'],organization['desc'])
        result['orgas'].append(added_orga)
      except ckanapi.ValidationError as e:
        traceback.print_exc()
        result['errors'].append(e)

    # Add admins to organizations
    for role in [{'organization':'mekong-organization','user':'odmmekong','role':'admin'},
                  {'organization':'cambodia-organization','user':'odmcambodia','role':'admin'},
                  {'organization':'laos-organization','user':'odmlaos','role':'admin'},
                  {'organization':'thailand-organization','user':'odmthailand','role':'admin'},
                  {'organization':'vietnam-organization','user':'odmvietnam','role':'admin'},
                  {'organization':'myanmar-organization','user':'odmmyanmar','role':'admin'}]:

      try:
        added_role = ckanapiutils.add_admin_to_organization(role['organization'],role['user'],role['role'])
        result['roles'].append(added_role)
      except ckanapi.ValidationError as e:
        traceback.print_exc()
        result['errors'].append(e)

    # Add Groups
    for group in [{'name':'maps-group','title':'Maps','desc':'Group for Maps'},
                  {'name':'news-group','title':'News','desc':'Group for News'},
                  {'name':'laws-group','title':'Laws','desc':'Group for Laws'}]:

      # Add groups
      try:
        added_group = ckanapiutils.add_group(group['name'],group['title'],group['desc'])
        result['groups'].append(added_group)
      except ckanapi.ValidationError as e:
        traceback.print_exc()
        result['errors'].append(e)

    return result
