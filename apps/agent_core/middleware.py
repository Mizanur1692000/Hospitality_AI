"""
Custom middleware to handle ngrok host validation dynamically
"""
import re
from django.http import HttpResponseBadRequest
from django.conf import settings


class NgrokHostMiddleware:
    """
    Middleware to dynamically allow ngrok hosts without restarting Django
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.ngrok_patterns = [
            r'.*\.ngrok-free\.app$',
            r'.*\.ngrok\.io$',
            r'.*\.ngrok\.app$',
        ]

    def __call__(self, request):
        # Check if the host is already allowed
        host = request.get_host().split(':')[0]  # Remove port if present

        # Allow localhost and 127.0.0.1
        if host in ['localhost', '127.0.0.1']:
            return self.get_response(request)

        # Check if host matches ngrok patterns
        for pattern in self.ngrok_patterns:
            if re.match(pattern, host):
                # Dynamically add to ALLOWED_HOSTS if not already there
                if host not in settings.ALLOWED_HOSTS:
                    settings.ALLOWED_HOSTS.append(host)
                    print(f"[MIDDLEWARE] Dynamically added {host} to ALLOWED_HOSTS")
                return self.get_response(request)

        # Check if host is in ALLOWED_HOSTS or matches wildcard
        if host in settings.ALLOWED_HOSTS or '*' in settings.ALLOWED_HOSTS:
            return self.get_response(request)

        # If we get here, the host is not allowed
        print(f"[MIDDLEWARE] Rejected request from host: {host}")
        return HttpResponseBadRequest(f"Invalid host: {host}")
