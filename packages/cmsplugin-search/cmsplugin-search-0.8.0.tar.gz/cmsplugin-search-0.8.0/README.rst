================
cmsplugin-search
================

Details:
=================
This package has been forked to work with current django-haystack 2.0, thanks to
the various patches and branches available that got most of this done.

This module been renamed to a more consistant name for cmsplugins and uploaded
to pypi so more people can use haystack 2.0 by Martin Owens <doctormo@gmail.com>

This package provides multilingual search indexes for easy Haystack integration
with django CMS.

Current support:
 * python 3.6
 * django 1.11.11
 * haystack 2.8.1

Language Notes:
===============

Instead of indexing each language as a seperate index, all pages/titles are
indexed you can then either search for all pages with any language or use a
filter with a custom SearchView class with an updated SearchQuerySet:

class SearchView(BaseView):
    def __call__(self, request):
        language = get_language_from_request(request)
        self.searchqueryset = SearchQuerySet().filter(language=language)
        return BaseView.__call__(self, request)

Usage
=====

After installing django-cms-search through your package manager of choice, add ``cms_search`` to your
``INSTALLED_APPS``

For setting up Haystack, please refer to their `documentation <http://docs.haystacksearch.org/dev/>`_.

For more docs, see the ``docs`` folder or the
`online documentation <http://django-cms-search.readthedocs.org/en/latest/>`_.
