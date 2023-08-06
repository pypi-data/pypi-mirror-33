"""
    https://stackoverflow.com/questions/24559531/how-do-i-restrict-access-to-admin-pages-in-django
    https://djangosnippets.org/snippets/2095/
"""
from django.http import Http404
from django.conf import settings

RESTRICTED_PATHS = getattr(settings, "RESTRICTED_PATHS", [])
IS_DEVELOPMENT = getattr(settings, "IS_DEVELOPMENT", False)

class RestrictedPathsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not IS_DEVELOPMENT:
            if not request.user.is_staff:
                for path in RESTRICTED_PATHS:
                    if request.path.startswith(path):
                        raise Http404
        return self.get_response(request)
