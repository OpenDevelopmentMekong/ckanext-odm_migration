import os
import csv
from collections import defaultdict

# Interface definition
class IDataApi:

  def load_data_from_csv(self):
    raise NotImplementedError

  def load_odc_laws(self,lang):
    raise NotImplementedError

  def load_marc21_records(self):
    raise NotImplementedError

# Mock implementation
class TestDataApi (IDataApi):

  def __init__(self):
    return

  def load_data_from_csv(self):
    return []

  def load_odc_laws(self,lang):
    return "<xml></xml>"

  def load_marc21_records(self):
    return ""

# Real implementation
class RealDataApi (IDataApi):

  def __init__(self):

    self.laws = {
      "en": "laws_en_2015-12-17.xml",
      "km": "laws_km_2015-12-17.xml"
    }

    return

  def load_data_from_csv(self,path):

    data = defaultdict(list)
    if (os.path.isfile(path) and path.endswith(".csv")):
      with open(path, 'r') as csvfile:
        fileDialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        myReader = csv.reader(csvfile, dialect=fileDialect)
        for row in myReader:
          key = row.pop(0)
          values = row[0].split(";")
          data[key] = values

    return dict(data)

  def load_odc_laws(self,lang):

    lawsfile = self.laws[lang]
    pathToFile = os.path.join(os.path.dirname(__file__), '../data/'+lawsfile)
    with open(pathToFile, 'r') as f:
      return f.read()

  def load_marc21_records(self):

    pathToFile = os.path.join(os.path.dirname(__file__), '../data/records.mrc')
    with open(pathToFile, 'r') as f:
      return f.read()
