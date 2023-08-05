from django.conf import settings

CLIENT_ID = getattr(settings, 'IMGUR_CLIENT_ID', None)
CLIENT_SECRET = getattr(settings, 'IMGUR_CLIENT_SECRET', None)
ACCESS_TOKEN = getattr(settings, 'IMGUR_ACCESS_TOKEN', None)
ACCESS_REFRESH_TOKEN = getattr(settings, 'IMGUR_REFRESH_TOKEN', None)
USERNAME = getattr(settings, 'IMGUR_USERNAME', None)
