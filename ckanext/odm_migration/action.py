import logging
import ckan.logic.action.update as update_core
from ckan import logic
import ckan.lib.navl.validators as validators
import ckan.lib.navl.dictization_functions
from six import text_type
import psycopg2
import time

log = logging.getLogger(__name__)
_check_access = logic.check_access
_validate = ckan.lib.navl.dictization_functions.validate
ValidationError = logic.ValidationError



def term_translation_update(context, data_dict):
    '''Create or update a term translation.

    You must be a sysadmin to create or update term translations.

    :param term: the term to be translated, in the original language, e.g.
        ``'romantic novel'``
    :type term: string
    :param term_translation: the translation of the term, e.g.
        ``'Liebesroman'``
    :type term_translation: string
    :param lang_code: the language code of the translation, e.g. ``'de'``
    :type lang_code: string

    :returns: the newly created or updated term translation
    :rtype: dictionary

    '''
    model = context['model']

    _check_access('term_translation_update', context, data_dict)

    schema = {'term': [validators.not_empty, text_type],
              'term_translation': [validators.not_empty, text_type],
              'lang_code': [validators.not_empty, text_type]}

    data, errors = _validate(data_dict, schema, context)
    if errors:
        model.Session.rollback()
        raise ValidationError(errors)

    trans_table = model.term_translation_table

    update = trans_table.update()
    update = update.where(trans_table.c.term == data['term'])
    update = update.where(trans_table.c.lang_code == data['lang_code'])
    update = update.values(term_translation = data['term_translation'])

    conn = model.Session.connection()
    result = conn.execute(update)

    # insert if not updated
    if not result.rowcount:
        conn.execute(trans_table.insert().values(**data))

    if not context.get('defer_commit'):
        model.Session.commit()
   
    return data

def term_translation_update_many(context, data_dict):
    '''Create or update many term translations at once.

    :param data: the term translation dictionaries to create or update,
        for the format of term translation dictionaries see
        :py:func:`~term_translation_update`
    :type data: list of dictionaries

    :returns: a dictionary with key ``'success'`` whose value is a string
        stating how many term translations were updated
    :rtype: string

    '''
    # Bug fix
    # This may translation will commit to database once all the translations are added.
    # Problem is uwsgi restarts in the middle and we will loose all the tranlsation before commit
    # Changed the API to commit in chunks default sie is 5000

    model = context['model']
    if not (data_dict.get('data') and isinstance(data_dict.get('data'), list)):
        raise ValidationError(
            {'error': 'term_translation_update_many needs to have a '
                      'list of dicts in field data'}
        )

    context['defer_commit'] = True
    action = term_translation_update
    log.info("********** Total: {}".format(len(data_dict['data'])))
    for num, row in enumerate(data_dict['data']):
        print(num)
        action(context, row)

    log.info("Committing translations....")
    model.Session.commit()

    return {'success': '%s rows updated' % (num + 1)}
