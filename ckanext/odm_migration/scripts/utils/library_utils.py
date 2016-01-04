import script_utils
import uuid

def _set_extras_from_record_to_ckan_dataset_dict(dataset_metadata,record,config):

  if dataset_metadata is None:
    return None

  # Spatial range
  dataset_metadata['odm_spatial_range'] = config.odm_spatial_range

  # Language
  dataset_metadata['odm_language'] = 'en'

  # ISBN
  if record.isbn():
    dataset_metadata['marc21_020'] = unicode(record.isbn())
  # ISSN
  if record['022']:
    dataset_metadata['marc21_022'] = unicode(record['022'].value())
  # Classification
  if record['084']:
    dataset_metadata['marc21_084'] = unicode(record['084'].value())
  # Author
  if record['100']:
    dataset_metadata['marc21_100'] = unicode(record['100'].value())
  # Corporate Author
  if record['110']:
    dataset_metadata['marc21_110'] = unicode(record['110'].value())
  # Varying Form of Title
  if record['246']:
    dataset_metadata['marc21_246'] = unicode(record['246'].value())
  # Edition
  if record['250']:
    dataset_metadata['marc21_250'] = unicode(record['250'].value())
  # Publication Name
  if record['260'] and record['260']['a']:
    dataset_metadata['marc21_260a'] = unicode(record['260']['a'])
  # Publication Place
  if record['260'] and record['260']['b']:
    dataset_metadata['marc21_260b'] = unicode(record['260']['b'])
  # Publication Date
  if record['260'] and record['260']['c']:
    dataset_metadata['marc21_260c'] = unicode(record['260']['c'])
  # Pagination
  if record.physicaldescription():
    dataset_metadata['marc21_300'] = unicode(','.join([e.value() for e in record.physicaldescription()]))
  # General Note
  if record.notes():
    dataset_metadata['marc21_500'] = unicode(','.join([e.value() for e in record.notes()]))
  # Subject
  if record.subjects():
    dataset_metadata['marc21_650'] = unicode(','.join([e.value() for e in record.subjects()]))
  # Subject (Geographic Name)
  if record['651']:
    dataset_metadata['marc21_651'] = unicode(record['651'].value())
  # Keyword
  if record['653']:
    dataset_metadata['marc21_653'] = unicode(','.join([e.value() for e in record.get_fields('653')]))
  # Added entries
  if record.addedentries():
    dataset_metadata['marc21_700'] = unicode(','.join([e.value() for e in record.addedentries()]))
  # Institution
  if record['850']:
    dataset_metadata['marc21_850'] = unicode(record['850'].value())
  # Location
  if record.location():
    dataset_metadata['marc21_852'] = unicode(','.join([e.value() for e in record.location()]))

  return dataset_metadata

def _map_record_to_ckan_dataset_dict(record,config):

  # First, extract the information from the layer (Title, Abstract, Tags)
  params_dict = {}
  params_dict['id'] = ''
  params_dict['state'] = 'active'

  # Specify the package_type
  params_dict['type'] = config.package_type

  params_dict['maintainer'] = config.IMPORTER_NAME
  params_dict['maintainer_email'] = config.IMPORTER_EMAIL

  try:

    if record.title():
      params_dict['title'] = record.title()

    if (record.title()) and (record.title() != ''):
      params_dict['name'] = script_utils._prepare_string_for_ckan_name(str(uuid.uuid5(uuid.NAMESPACE_DNS, record.title().encode('utf-8'))))
    elif record.isbn() and (record.isbn() != ''):
      params_dict['name'] = script_utils._prepare_string_for_ckan_name(record.isbn())
    else:
      return None

    if (not record.title()) or (record.title() == ''):
      params_dict['title'] = params_dict['name']

  except UnicodeEncodeError as e:
    if (config.DEBUG):
      traceback.print_exc()

  # Summary
  if record['520']:
    params_dict['notes'] = unicode(record['520'].value())

  return params_dict
