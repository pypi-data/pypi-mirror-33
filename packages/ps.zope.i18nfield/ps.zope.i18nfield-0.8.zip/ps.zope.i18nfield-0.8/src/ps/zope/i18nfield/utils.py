# -*- coding: utf-8 -*-
"""Helper methods for the I18N field."""

from ps.zope.i18nfield.interfaces import ILanguageAvailability
from zope.component import queryUtility
from zope.globalrequest import getRequest
from zope.i18n.negotiator import negotiator

import codecs


DEFAULT_LANGUAGE = u'en'


def to_unicode(value, default=u''):
    """Get specified value converted to unicode, or an empty unicode string if
    value is empty

    :param value: [required] text to be checked
    :type value: str or unicode
    :param default: default value
    :return: value, or default if value is empty
    :rtype: unicode
    """
    try:
        if isinstance(value, unicode):
            return value
        return codecs.decode(value or default)
    except Exception:
        return codecs.decode(value or default, 'latin1')


def get_language(request=None):
    if request is None:
        request = getRequest()
    try:
        return negotiator.getLanguage(available_languages(), request)
    except TypeError:
        return get_default_language()


def get_default_language():
    """Return the default fallback languages."""
    utility = queryUtility(ILanguageAvailability)
    if utility is not None:
        return utility.getDefaultLanguage()
    return DEFAULT_LANGUAGE


def available_languages():
    """Return a list of available languages."""
    utility = queryUtility(ILanguageAvailability)
    if utility is not None:
        return utility.getAvailableLanguages()
    return [DEFAULT_LANGUAGE]


def sorted_languages():
    utility = queryUtility(ILanguageAvailability)
    if utility is not None:
        return utility.get_sorted_languages()
    available = available_languages()
    tmp_languages = sorted([unicode(key) for key in available])
    languages = []
    if u'en' in tmp_languages:
        tmp_languages.remove(u'en')
        languages.append(u'en')
    if u'es' in tmp_languages:
        tmp_languages.remove(u'es')
        languages.append(u'es')
    languages.extend(tmp_languages)
    return languages
