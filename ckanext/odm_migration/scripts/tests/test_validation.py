import os
from nose.tools import assert_equal, assert_in

class TestValidation:

  def test_01_data_available(self):

    assert os.path.isdir(os.path.abspath(os.path.join(__file__, '../../','data')))
    assert os.path.isfile(os.path.abspath(os.path.join(__file__, '../../','data/laws_en_2015-12-17.xml')))
    assert os.path.isfile(os.path.abspath(os.path.join(__file__, '../../','data/laws_km_2015-12-17.xml')))
    assert os.path.isfile(os.path.abspath(os.path.join(__file__, '../../','data/records.mrc')))
    assert os.path.isfile(os.path.abspath(os.path.join(__file__, '../../','data/taxonomy_map.csv')))
