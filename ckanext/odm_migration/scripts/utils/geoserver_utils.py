# -*- coding: utf-8 -*-
''' Module containing classes and methods for interaction with geoserver

'''
import json
import urllib2
import urllib

# Interface definition
class IGeoserverRestApi:

  def get_layers(self):
    raise NotImplementedError

  def get_geojson_from_url(self,url):
    raise NotImplementedError

  def download_file(self,src,dest):
    raise NotImplementedError

# Mock implementation
class TestGeoserverRestApi (IGeoserverRestApi):

  def __init__(self):

    self.geoserver_url = ''
    self.geoserver_auth = ''

    return

  def get_layers(self):

    # return JSON dictionary
    json_string = '<layers><layer><name>Agriculture_Fishing:map_rice_ecosystem_kh</name><atom:link xmlns:atom="http://www.w3.org/2005/Atom" rel="alternate" href="http://geoserver.opendevelopmentmekong.net/geoserver/gwc/rest/layers/Agriculture_Fishing%3Amap_rice_ecosystem_kh.xml" type="text/xml"/></layer></layers>'
    return json_string

  def get_geojson_from_url(self,url):

    # return JSON dictionary
    json_string = '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[102,0.6]},"properties":{"prop0":"value0"}},{"type":"Feature","geometry":{"type":"LineString","coordinates":[[102,0],[103,1],[104,0],[105,1]]},"properties":{"prop1":0,"prop0":"value0"}},{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[100,0],[101,0],[101,1],[100,1],[100,0]]]},"properties":{"prop1":{"this":"that"},"prop0":"value0"}}]}'
    return json.loads(json_string)

  def download_file(self,src,dest):
    with open(dest, 'w') as outfile:
      outfile.write('Sample file contents')


# Real implementation
class RealGeoserverRestApi (IGeoserverRestApi):

  def __init__(self,config):

    # Init here
    self.geoserver_url = config.GEOSERVER_URL
    self.geoserver_auth = config.GEOSERVER_AUTH

    return

  def get_layers(self):

    request = urllib2.Request(self.geoserver_url+'gwc/rest/layers.xml')
    request.add_header('Authorization', self.geoserver_auth)

    # Make the HTTP request.
    response = urllib2.urlopen(request)
    assert response.code == 200

    # return XML content
    return response.read()

  def get_feature_type_layer(self, feature_name):
    # feature_name: feature_namespace:feature_name eg. Energy:Hydropower_dams
    request = urllib2.Request(self.geoserver_url+'rest/layers/'+feature_name+'.xml')
    request.add_header('Authorization', self.geoserver_auth)

    # Make the HTTP request.
    response = urllib2.urlopen(request)
    assert response.code == 200

    # return XML content
    return response.read()

  def get_feature_type_info(self, feature_context):
       for event, elem in feature_context:
           if event == "end" and elem.tag == "resource":
               if (elem.find('{http://www.w3.org/2005/Atom}link') is not None):
                   feature_type_layer_url = elem.find('{http://www.w3.org/2005/Atom}link').get('href')
                   # feature_type_layer_url: The url to get all informtion of individual layer such as workspace, store, title and name.
                   request = urllib2.Request(feature_type_layer_url)
                   request.add_header('Authorization', self.geoserver_auth)

                   # Make the HTTP request.
                   response = urllib2.urlopen(request)
                   assert response.code == 200
                   # return XML content
                   return response.read()

  def get_geojson_from_url(self,url):

    request = urllib2.Request(url)
    request.add_header('Authorization', self.geoserver_auth)

    # Make the HTTP request.
    response = urllib2.urlopen(request)
    assert response.code == 200

    # return JSON dictionary
    return json.loads(response.read())

  def download_file(self,src,dest):

    urllib.urlretrieve (src,dest)
