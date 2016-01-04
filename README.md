# ckanext-odm-migration

CKAN extension exposing scripts for migration from previous ODC site to the new server.

# Contents

## Ckan scripts

A series of python scripts that help importing contents from previous systems into CKAN, such as Taxonomy terms and translations, map layers from geoserver, library records from NGL or contents exported from Wordpress in XML format. Also, there are a series of utility methods to do bulk operations in CKAN such as delete datasets in a group, insert initial data or change datasets type programatically.

### Install dependencies

In order to run the import scripts the dependencies specified in the **requirements.txt** need to be installed ( i.e. using pip)

```
pip install -r requirements
```

### Testing the scripts

Run ```nosetests```

# Copyright and License

This material is copyright (c) 2014-2015 East-West Management Institute, Inc. (EWMI).

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
