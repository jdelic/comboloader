# -* coding: utf-8 *-
import logging
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def __require_envvar(name):
    if os.getenv(name, None):
        return os.getenv(name)
    else:
        raise ImproperlyConfigured("Undefined environment variable %s" % name)


def __append_optional_module(module_list, name):
    try:
        __import__(name)
    except ImportError:
        pass 
    else:
        module_list.append(name)


if os.getenv("LOG_CONFIG", None):
    logging.config.fileConfig(os.getenv("LOG_CONFIG"))
else:
    logging.basicConfig()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = __require_envvar("SECRET_KEY") 

STATIC_URL = "/static/"

INSTALLED_APPS = [
    "django.contrib.staticfiles",
]

__append_optional_module(INSTALLED_APPS, "raven.contrib.django.raven_compat")
__append_optional_module(INSTALLED_APPS, "pipeline")

ROOT_URLCONF = "comboloader.urls"

WSGI_APPLICATION = "comboloader.wsgi.application"

DATABASES = {}

CACHES = {
    "default": django_cache_url.parse(__require_envvar("CACHE_URL")),
}

_jslibs_path = os.getenv("BASEDIR", None)
if not _jslibs_path and not DEBUG:
    raise ImproperlyConfigured("Undefined environment variable BASEDIR")

CACHETTL = os.getenv("CACHETTL", None)
if CACHETTL:
    try:
        CACHETTL = int(CACHETTL)
    except ValueError:
        logging.error("CACHETTL is not a number (%s)", CACHETTL)
elif not COMBOLOADER_CACHETTL and not DEBUG:
    logging.warning("comboloader configured as non-caching")

LIBRARIES = {
    "": {
        "path": _jslibs_path,
    }
}

for k, v in os.environ.items():
    if k.startswith("COMBOLIB_"):
        lib = k[len("COMBOLIB_"):].lower()
        LIBRARIES[lib] = {
            "path": v,
        }

# use logging module, because django logging isn"t set up yet
logging.info("Configured for: %s", ", ".join(LIBRARIES.keys()))
if CACHETTL:
    logging.info("Caching for %s seconds", CACHETTL)

