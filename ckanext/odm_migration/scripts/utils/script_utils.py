import datetime
import re
import urlparse
import os
import uuid
import urllib

def _set_mandatory_metadata_fields(dataset_metadata,trace):

  dataset_metadata['import_trace'] = trace

  dataset_metadata['license_title'] = 'License unspecified'
  dataset_metadata['license_id'] = 'unspecified'
  dataset_metadata['version'] = '1.0'
  dataset_metadata['maintainer'] = 'OD Mekong Importer'
  dataset_metadata['maintainer_email'] = 'info@opendevmekong.net'
  dataset_metadata['odm_date_created'] = datetime.date.today().strftime("%m/%d/%y")
  dataset_metadata['odm_date_uploaded'] = datetime.date.today().strftime("%m/%d/%y")
  dataset_metadata['odm_process'] = 'Imported via scripts'
  dataset_metadata['odm_source'] = 'Imported via scripts'

  return dataset_metadata

def _set_mandatory_metadata_multilingual_fields(dataset_metadata,lang):

  odm_contact = {}
  if 'odm_contact' in dataset_metadata:
    odm_contact = dataset_metadata['odm_contact']

  odm_contact[lang] = 'Open Development Cambodia http://www.opendevelopmentcambodia.net'
  dataset_metadata['odm_contact'] = odm_contact

def _inspect_json_dict_fill_list(inspected_dict,term_list):

  # Append name to term_list from each of the nodes, indepently of whether they are node or leaf
  term_list.append(inspected_dict['name'])

  # Then try to go deeper recursively
  if 'children' in inspected_dict.keys():

    # Has children
    for child in inspected_dict['children']:

      # Iterate deeper
      _inspect_json_dict_fill_list(child,term_list)

def _is_key_in_fields(key,fields):

  for field in fields:
    if key == field[0]:
      return True

  return False

def _cap_string(string, length):
  return string if len(string)<=length else string[0:length-1]

def _prepare_string_for_ckan_tag_name(string):
  string = ''.join(ch for ch in string if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' ' ))
  string = _cap_string(string,100)
  return string

def _prepare_string_for_ckan_taxonomy_name(string):
 string = ''.join(ch for ch in string if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' ' ))
 #string = string.replace(' ','_').lower()
 string = _cap_string(string,100)
 return string

def _prepare_string_for_ckan_name(string):
  string = ''.join(ch for ch in string if (ch.isalnum() or ch == '_' or ch == '-'))
  string = string.replace(' ','_').lower()
  string = _cap_string(string,100)
  return string

def _prettify_name(string):
  return string.replace('_',' ').encode('utf-8')

def _capitalize_name(string):
  return _prettify_name(string.title())

def _is_unicode(string):
  return isinstance(string, unicode)

def _is_valid_url(url):
  regex = re.compile(
      r'^https?://'  # http:// or https://
      r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
      r'localhost|'  # localhost...
      r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
      r'(?::\d+)?'  # optional port
      r'(?:/?|[/?]\S+)$', re.IGNORECASE)
  return url is not None and regex.search(url)

def _contains_non_utf8(string):
  try:
    string.decode('UTF-8', 'strict')
  except UnicodeDecodeError:
    return True

  return False

def _get_ext(url):
  parsed = urlparse.urlparse(url)
  root, ext = os.path.splitext(parsed.path)
  return ext[1:]  # or ext[1:] if you don't want the leading '.'

def _download_file(url,dest):
  urllib.urlretrieve(url,dest)

def _str_capitalize_underscore_replaced_with_space( string):
  string = string.replace("_", " ")
  return string.capitalize()

def _generate_temp_filename(ext):
  return str(uuid.uuid4()) + "." + str(ext)

def _create_metadata_dictionary_for_upload(dataset_id,url,path,name,description,format,lang):

  dataset_metadata = dict({})
  dataset_metadata['package_id'] = dataset_id
  dataset_metadata['url'] = url
  dataset_metadata['upload'] = path
  dataset_metadata['name'] = _prettify_name(name)
  dataset_metadata['description'] = description
  dataset_metadata['format'] = format

  if lang:
    odm_language = [lang]
    dataset_metadata['odm_language'] = odm_language

  return dataset_metadata

def _generate_wms_download_url(geoserver_url,namespace,title,file_format):

  file_url = '<geoserver><namespace>/wms?service=WMS&version=1.1.0&request=GetMap&layers=<namespace>:<title>&styles=&bbox=211430.86563420878,1144585.4696614784,784623.3606298851,1625594.694892376&width=<width>&height=<height>&srs=EPSG:32648&format=<format>'
  file_url = file_url.replace('<geoserver>',geoserver_url)
  file_url = file_url.replace('<namespace>',namespace)
  file_url = file_url.replace('<format>',file_format)
  file_url = file_url.replace('<title>',title)
  file_url = file_url.replace('<width>','512')
  file_url = file_url.replace('<height>','429')

  return file_url

def _create_metadata_dictionary_for_resource(dataset_id,url,name,description,format):

  dataset_metadata = dict({})
  dataset_metadata['package_id'] = dataset_id
  dataset_metadata['url'] = url
  dataset_metadata['name'] = _prettify_name(name)
  dataset_metadata['description'] = description
  dataset_metadata['format'] = format

  return dataset_metadata

def _generate_ows_download_url(geoserver_url,namespace,title,file_format):

  file_url = '<geoserver><namespace>/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=<namespace>:<title>&srsName=EPSG:4326&outputFormat=<format>'
  file_url = file_url.replace('<geoserver>',geoserver_url)
  file_url = file_url.replace('<namespace>',namespace)
  file_url = file_url.replace('<format>',file_format)
  file_url = file_url.replace('<title>',title)
  file_url = file_url.replace('<width>','512')
  file_url = file_url.replace('<height>','429')

  return file_url
