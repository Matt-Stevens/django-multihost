"""
Provides utilities to help multi-site aware Django projects.
"""
from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models.loading import app_cache_ready
from django.db.models import Q
from django.core.cache import cache
from multihost import get_current_request
import operator


def by_host(host=None, recursion=False):
    """
    Get the current site by looking at the request stored in the thread.

    Returns the best match found in the `django.contrib.sites` app.  If not
    found, then returns the default set as given in `settings.SITE_ID`

    Params:
     - `host`: optional, host to look up
     - `recursion`: used to prevent an endless loop of calling this function
    """
    site = None
    # if the host value wasn't passed in,
    # take a look inside the request for data
    if not host:
        request = get_current_request()

        if request:
            # if the request object already has the site set, return it
            if hasattr(request, 'site'):
                # if the request.site value isn't of type Site, return it,
                # as the developer using this app is doing something funky
                if not isinstance(request.site, Site):
                    return request.site

                return request.site
            else:
                host = request.get_host()

    if host:
        if app_cache_ready():
            key = 'SITE_{0}'.format(host)

            # try to get the Site out of Django's cache
            site = cache.get(key)
            if not site:
                site = lookup(site, host, recursion)

                # if we finally have the Site, save it in the cache
                if site:
                    cache.set(key, site)
        else:
            site = lookup(site, host, recursion)

    return site


def lookup(site, host, recursion):
    """
    This does the actual lookup of the `Site` object.
    """
    try:
        filters = [Q(domain=host), ]

        # if a port is specified
        if host.find(':') != -1:
            filters.append(Q(domain=host.split(':')[0]))

        site = Site.objects.filter(reduce(operator.or_, filters))[0]
    except IndexError:
        pass

    # if the Site still hasn't been found, add or remove the 'www.'
    # from the host and try with that.
    multihost_auto_www = getattr(settings, 'MULTIHOST_AUTO_WWW', True)

    if not recursion and not site and multihost_auto_www:
        host = host[4:] if host.startswith('www.') else 'www.{0}'.format(host)
        site = by_host(host=host, recursion=True)

    return site
