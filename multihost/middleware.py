from django.contrib.sites.models import SiteManager
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.conf import settings
from multihost import sites
from multihost import set_thread_variable


class MultiHostMiddleware(object):
    """
    Middleware to detect the incoming hostname and
    take a specified action based on its value.
    """
    def __init__(self):
        """
        This function overrides the get_current() method of the
        SiteManager so that it can be more robust in detecting
        incoming Host headers and finding matching Site instances.

        You can override the functionality in this function by
        creating your own in settings.
        """
        def site_get_current(self):
            return sites.by_host()

        SiteManager.get_current = site_get_current

    def process_request(self, request):
        """
        This stores the request object in threadlocal storage so that it
        can be accessed from within our Site.objects.get_current()
        method (above) as it does not have access to the request instance.

        Using the new get_current(), it gets the Site matching the Host
        header and stores it in the request instances if found. If it
        returned the default site (SITE_ID), then it failed to find a
        match, and we redirect to a safe location.
        """
        set_thread_variable('request', request)

        site = Site.objects.get_current()

        # No matching `Site` object found
        if not site:
            # this will intentionally raise an exception if the user does not
            # have a default redirect URL in `MULTIHOST_REDIRECT_URL`.
            return HttpResponseRedirect(getattr(settings, 'MULTIHOST_REDIRECT_URL'))

        # Attach `Siet` object to the request for use in other middleware and views
        request.site = site

        return None
