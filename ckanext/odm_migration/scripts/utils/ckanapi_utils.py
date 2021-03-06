# -*- coding: utf-8 -*-
''' Module containing classes and methods for interaction with ckanapi

'''
import ckanapi
import requests
from ckan.common import config as ckan_config
import ckan.lib.base as base
context = base.c

# Interface definition
class ICkanApi:

  def search_packages(self,params):
    raise NotImplementedError

  def get_package_list(self,params):
    raise NotImplementedError

  def get_organization_id_from_name(self,organization):
    raise NotImplementedError

  def add_organization(self,organization,title,description):
    raise NotImplementedError

  def add_group(self,group,title,description):
    raise NotImplementedError

  def add_user(self,name,email,password,about):
    raise NotImplementedError

  def add_admin_to_organization(self,organization,username,role):
    raise NotImplementedError

  def get_package_contents(self,name):
    raise NotImplementedError

  def update_package(self,params):
    raise NotImplementedError

  def patch_package(self,params):
    raise NotImplementedError

  def create_package(self,params):
    raise NotImplementedError

  def create_resource(self,params):
    raise NotImplementedError

  def create_resource_with_file_upload(self,params):
    raise NotImplementedError

  def create_tag(self,params):
    raise NotImplementedError

  def create_tag_vocabulary(self,params):
    raise NotImplementedError

  def update_tag_vocabulary(self,params):
    raise NotImplementedError

  def delete_tag_vocabulary(self,params):
    raise NotImplementedError

  def show_tag_vocabulary(self,params):
    raise NotImplementedError

  def get_all_tags_from_tag_vocabulary(self,params):
    raise NotImplementedError

  def exists_taxonomy_tag_dictionaries(self,params):
    raise NotImplementedError

  def add_term_translation(self,params):
    raise NotImplementedError

  def add_term_translation_many(self,params):
    raise NotImplementedError

  def get_packages_in_group(self,params):
    raise NotImplementedError

  def get_packages_in_organization(self,params):
    raise NotImplementedError

  def delete_packages_list(self,params):
    raise NotImplementedError

  def create_default_issue(self,params):
    raise NotImplementedError

# Mock implementation
class TestCkanApi (ICkanApi):

  def __init__(self,test_app,context):

    # Init here
    self.test_app = test_app
    self.ckan_auth = context['apikey']
    self.api = ckanapi.TestAppCKAN(self.test_app,apikey=self.ckan_auth)

  def search_packages(self,params):

    return self.api.call_action('package_search',params)

  def get_package_list(self,params):

    return self.api.call_action('package_list',params)

  def get_organization_id_from_name(self,organization):

    return self.api.action.organization_show(id=organization,include_datasets=False)

  def add_organization(self,organization,title,description):

    return self.api.action.organization_create(name=organization,title=title,description=description)

  def add_group(self,group,title,description):

    return self.api.action.group_create(name=group,title=title,description=description)

  def add_user(self,name,email,password,about):

    return self.api.action.user_create(name=name,email=email,password=password,about=about)

  def add_admin_to_organization(self,organization,username,role):

    return self.api.action.organization_member_create(id=organization,username=username,role=role)

  def get_package_contents(self,name):

    return self.api.action.package_show(id=name)

  def update_package(self,params):

    return self.api.call_action('package_update',params)

  def patch_package(self,params):

    return self.api.patch.call_action('package_patch',params)

  def create_package(self,params):

    return self.api.call_action('package_create',params)

  def create_resource(self,params):

    return self.api.call_action('resource_create',params)

  def create_resource_with_file_upload(self,params):

    return True

  def create_tag(self,params):

    return self.api.call_action('tag_create',params)

  def create_tag_vocabulary(self,params):

    return self.api.call_action('vocabulary_create',params)

  def update_tag_vocabulary(self,params):

    return self.api.call_action('vocabulary_update',params)

  def delete_tag_vocabulary(self,params):

    return self.api.call_action('vocabulary_delete',params)

  def show_tag_vocabulary(self,params):

    return self.api.call_action('vocabulary_show',params)

  def get_all_tags_from_tag_vocabulary(self,params):

    return self.api.call_action('tag_list',params)

  def exists_taxonomy_tag_dictionaries(self,params):

    try:

      return self.api.call_action('vocabulary_show',id=params['id'])

    except ckanapi.NotFound:

      return None

  def add_term_translation(self,params):

    return self.api.call_action('term_translation_update',params)

  def add_term_translation_many(self,params):

    return self.api.call_action('term_translation_update_many',params)

  def get_packages_in_group(self,params):

    return self.api.call_action('group_package_show',params)

  def get_packages_in_organization(self,params):

    result = self.api.action.organization_show(id=params['id'],include_datasets=True)

    return result['packages']

  def delete_packages_list(self,params):

    return self.api.call_action('bulk_update_delete',params)

  def create_default_issue(self,params):

    return self.api.call_action('issue_create',params)

# Real implementation
class RealCkanApi (ICkanApi):

  def __init__(self,config):

    # Init here
    self.ckan_url = config.CKAN_URL
    self.ckan_auth = config.CKAN_APIKEY
    self.api = ckanapi.RemoteCKAN(self.ckan_url,apikey=self.ckan_auth)

    return

  def search_packages(self,params):

    return self.api.call_action('package_search',params,requests_kwargs={'verify':False})

  def get_package_list(self,params):

    return self.api.call_action('package_list',params,requests_kwargs={'verify':False})

  def get_organization_id_from_name(self,organization):

    params = {'id':organization,'include_datasets':False}
    return self.api.call_action('organization_show',params,requests_kwargs={'verify':False})

  def add_organization(self,organization,title,description):

    params = {'name':organization,'title':title,'description':description}
    return self.api.call_action('organization_create',params,requests_kwargs={'verify':False})

  def add_group(self,group,title,description):

    params = {'name':group,'title':title,'description':description}
    return self.api.call_action('group_create',params,requests_kwargs={'verify':False})

  def add_user(self,name,email,password,about):

    params = {'name':name,'email':email,'password':password,'about':about}
    return self.api.call_action('user_create',params,requests_kwargs={'verify':False})

  def add_admin_to_organization(self,organization,username,role):

    params = {'id':organization,'username':username,'role':role}
    return self.api.call_action('organization_member_create',params,requests_kwargs={'verify':False})

  def get_package_contents(self,name):

    params = {'id':name}
    return self.api.call_action('package_show',params,requests_kwargs={'verify':False})

  def update_package(self,params):

    return self.api.call_action('package_update',params,requests_kwargs={'verify':False})

  def patch_package(self,params):

    return self.api.patch.call_action('package_patch',params,requests_kwargs={'verify':False})

  def create_package(self,params):

    return self.api.call_action('package_create',params,requests_kwargs={'verify':False})

  def create_resource(self,params):

    return self.api.call_action('resource_create',params,requests_kwargs={'verify':False})

  def create_resource_with_file_upload(self,params):

    return requests.post(self.ckan_url + '/api/3/action/resource_create',verify=False,data=params,headers={"X-CKAN-API-Key": self.ckan_auth},files=[('upload', file(params["upload"]))])

  def create_tag(self,params):

    return self.api.call_action('tag_create',params,requests_kwargs={'verify':False})

  def create_tag_vocabulary(self,params):

    return self.api.call_action('vocabulary_create',params,requests_kwargs={'verify':False})

  def update_tag_vocabulary(self,params):

    return self.api.call_action('vocabulary_update',params,requests_kwargs={'verify':False})

  def delete_tag_vocabulary(self,params):

    return self.api.call_action('vocabulary_delete',params,requests_kwargs={'verify':False})

  def show_tag_vocabulary(self,params):

    return self.api.call_action('vocabulary_show',params,requests_kwargs={'verify':False})

  def get_all_tags_from_tag_vocabulary(self,params):

    return self.api.call_action('tag_list',params,requests_kwargs={'verify':False})

  def exists_taxonomy_tag_dictionaries(self,params):

    try:

      return self.api.call_action('vocabulary_show',id=params['id'],requests_kwargs={'verify':False})

    except ckanapi.NotFound:

      return None

  def add_term_translation(self,params):

    return self.api.call_action('term_translation_update',params,requests_kwargs={'verify':False})

  def add_term_translation_many(self,params):

    return self.api.call_action('term_translation_update_many',params,requests_kwargs={'verify':False})

  def get_packages_in_group(self,params):

    return self.api.call_action('group_package_show',params,requests_kwargs={'verify':False})

  def get_packages_in_organization(self,params):

    result = self.api.call_action('organization_show',{'id':params['id'],'include_datasets':True},requests_kwargs={'verify':False})

    return result['packages']

  def delete_packages_list(self,params):

    return self.api.call_action('bulk_update_delete',params,requests_kwargs={'verify':False})

  def create_default_issue(self,params):

    return self.api.call_action('issue_create',params,requests_kwargs={'verify':False})

# Local implementation
class LocalCkanApi (ICkanApi):

  def __init__(self):

    # Init here
    self.api = ckanapi.LocalCKAN()

    return

  def search_packages(self,params):

    return self.api.call_action('package_search',params)

  def get_package_list(self,params):

    return self.api.call_action('package_list',params)

  def get_organization_id_from_name(self,organization):

    params = {'id':organization,'include_datasets':False}
    return self.api.call_action('organization_show',params)

  def add_organization(self,organization,title,description):

    params = {'name':organization,'title':title,'description':description}
    return self.api.call_action('organization_create',params)

  def add_group(self,group,title,description):

    params = {'name':group,'title':title,'description':description}
    return self.api.call_action('group_create',params)

  def add_user(self,name,email,password,about):

    params = {'name':name,'email':email,'password':password,'about':about}
    return self.api.call_action('user_create',params)

  def add_admin_to_organization(self,organization,username,role):

    params = {'id':organization,'username':username,'role':role}
    return self.api.call_action('organization_member_create',params)

  def get_package_contents(self,name):

    params = {'id':name}
    return self.api.call_action('package_show',params)

  def update_package(self,params):

    return self.api.call_action('package_update',params)

  def patch_package(self,params):

    return self.api.patch.call_action('package_patch',params)

  def create_package(self,params):

    return self.api.call_action('package_create',params)

  def create_resource(self,params):

    return self.api.call_action('resource_create',params)

  def create_resource_with_file_upload(self,params):

    ckan_url = ckan_config.get("ckan.site_url", "")
    userobj = context.userobj
    ckan_auth = userobj.apikey

    return requests.post(ckan_url + 'api/3/action/resource_create',data=params,headers={"X-CKAN-API-Key": ckan_auth},files=[('upload', file(params["upload"]))],verify=False)

  def create_tag(self,params):

    return self.api.call_action('tag_create',params)

  def create_tag_vocabulary(self,params):

    return self.api.call_action('vocabulary_create',params)

  def update_tag_vocabulary(self,params):

    return self.api.call_action('vocabulary_update',params)

  def delete_tag_vocabulary(self,params):

    return self.api.call_action('vocabulary_delete',params)

  def show_tag_vocabulary(self,params):

    return self.api.call_action('vocabulary_show',params)

  def get_all_tags_from_tag_vocabulary(self,params):

    return self.api.call_action('tag_list',params)

  def exists_taxonomy_tag_dictionaries(self,params):

    try:

      return self.api.call_action('vocabulary_show',id=params['id'])

    except ckanapi.NotFound:

      return None

  def add_term_translation(self,params):

    return self.api.call_action('term_translation_update',params)

  def add_term_translation_many(self,params):

    return self.api.call_action('term_translation_update_many',params)

  def get_packages_in_group(self,params):

    return self.api.call_action('group_package_show',params)

  def get_packages_in_organization(self,params):

    result = self.api.call_action('organization_show',{'id':params['id'],'include_datasets':True})

    return result['packages']

  def delete_packages_list(self,params):

    return self.api.call_action('bulk_update_delete',params)

  def create_default_issue(self,params):

    return self.api.call_action('issue_create',params)
