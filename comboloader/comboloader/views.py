# -* coding: utf-8 *-
import logging
import os
import urllib

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.cache import cache_page, cache_control
from django.views.generic.base import View
from functools import wraps


_logger = logging.getLogger("djamboloader")

SUPPORTED_FILE_TYPES = {
    '.css': 'text/css',
    '.js':  'application/javascript',
}


class HealthCheck(View):
    """
    Monitoring tools call /health and expect a response with a status of 200
    in order to decide which applications are currently up and working.
    """
    def get(self, request):
        return HttpResponse('ok')

    def options(self, request):
        return HttpResponse('ok')


def _cache_library(load_view):
    """Caches the page if 'cache_for' is set in settings"""

    @wraps(load_view)
    def wrapper(request):
        if settings.JSCOMBO_CACHETTL is not None:
            cached_load_view = cache_page(settings.JSCOMBO_CACHETTL)(load_view)
            return cached_load_view(request)
        else:
            return load_view(request)

    return wrapper


def _combine(files):
    """
    Loads files from filesystem and combines them into one string
    input: list of files within given path (see constructor)
    output: combined result of all files
    """
    if not files:
        return ''

    content = ''

    for fn in files:
        try:
            f = open(fn, 'r')
            content += f.read()
            f.close()
        except IOError, e:
            _logger.error(e)
            raise

    return content


def _sanitize_filepath(path):
    # http://www.guyrutenberg.com/2013/12/06/preventing-directory-traversal-in-python/
    return os.path.normpath('/' + path).lstrip('/')


@cache_control(public=True)
@vary_on_headers('Accept-Encoding')
@_cache_library
def load(request):
    """
    Django view to load and combine a list of javascript/css files passed
    as GET query parameters for the given library.
    """
    libs = None
    mimetype = None

    if request.META:
        libstr = urllib.unquote_plus(request.META.get('QUERY_STRING', None))

    # Process and validate query parameters
    if libstr:
        if libstr.count('&') > 500:
            return HttpResponseBadRequest('Less than 500 files please')
        libs = libstr.split('&')

    if not libs:
        _logger.error('Missing parameters')
        return HttpResponseBadRequest('Missing parameters')

    selected_ext = None
    for ext, mimetype in SUPPORTED_FILE_TYPES.iteritems():
        if libs[0].endswith(ext):
            selected_ext = ext
            break

    if selected_ext is None:
        _logger.error("Unknown extension")
        return HttpResponseBadRequest()

    for lib in libs:
        if not lib.endswith(selected_ext):
            _logger.error("All parameters must be of the same type")
            return HttpResponseBadRequest()
        if lib.startswith('/'):
            return HttpResponseBadRequest()

    files = []
    for lib in libs:
        library = lib[0:lib.find('/')]
        basepath = settings.LIBRARIES['']['path']
        if library in settings.LIBRARIES:
            lib = lib[lib.find('/')+1:]
            basepath = settings.LIBRARIES[library.lower()]['path']

        absolute_path = os.path.join(basepath, _sanitize_filepath(lib))
        if os.path.exists(absolute_path):
            files.append(absolute_path)
        else:
            return HttpResponseNotFound('Library not found. %s %s %s' % (absolute_path, library, lib))

    try:
        response = _combine(files)
        return HttpResponse(response, content_type=mimetype)
    except IOError:
        return HttpResponseNotFound('Could not read file.')

