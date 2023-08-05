from django import template
from djcms_blog.models import Blog
from django.core.urlresolvers import reverse
from django.conf import settings

register = template.Library()


@register.simple_tag(name="blog_url")
def get_blog_url():
    blog = Blog.objects.first()
    if blog:
        return reverse("blog-main", kwargs={"blog_slug": blog.slug})
    if settings.djcms_blog_DEFAULT_URL:
        return settings.djcms_blog_DEFAULT_URL
    return "#"
