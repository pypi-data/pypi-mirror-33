from django.conf import settings


DJCMS_BLOG_DEFAULT_URL = getattr(settings, "DJCMS_BLOG_DEFAULT_URL", None)

DJCMS_BLOG_CACHE_TIME = getattr(settings, "DJCMS_BLOG_CACHE_TIME", 60 * 60 * 24)
