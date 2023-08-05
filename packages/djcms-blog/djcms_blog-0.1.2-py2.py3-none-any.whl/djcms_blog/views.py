from django.views.generic import DetailView
from django.utils.translation import gettext as _
from django.conf import settings
from django.http import Http404

from .models import Author, Blog, Tag, Post


class BlogDetailView(DetailView):
    language = None

    def get_language_code(self, url_path=None):
        default_lang = settings.LANGUAGES[0][0]
        if url_path is None:
            return default_lang
        lang_code = url_path.split("/")[1]
        return lang_code

    def set_language(self):
        self.language = self.get_language_code(self.request.META["PATH_INFO"])


class BlogView(BlogDetailView):
    template_name = "djcms_blog/blog.html"
    slug_field = "slug"
    slug_url_kwarg = "blog_slug"
    model = Blog

    def get_context_data(self, **kwargs):
        context = super(BlogView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        self.set_language()
        self.object = self.get_object()
        lang_object = self.object.get_language_object(self.language)
        self.object.description = lang_object.description
        self.object.meta_title = lang_object.meta_title
        self.object.meta_description = lang_object.meta_description
        self.object.get_posts = self.object.get_posts()
        for post in self.object.get_posts:
            post_object = post.language_object(self.language)
            post.title = post_object.title
            post.description = post_object.description
            post.published_date = post_object.published_date
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class TagView(BlogDetailView):
    template_name = "djcms_blog/tag.html"
    slug_field = "slug"
    slug_url_kwarg = "tag_slug"
    model = Tag

    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        self.set_language()
        self.object = self.get_object()
        lang_object = self.object.get_language_object(self.language)
        self.object.description = lang_object.description
        self.object.meta_title = lang_object.meta_title
        self.object.meta_description = lang_object.meta_description
        self.object.get_posts = self.object.get_posts()
        for post in self.object.get_posts:
            post_object = post.language_object(self.language)
            post.title = post_object.title
            post.description = post_object.description
            post.published_date = post_object.published_date
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class AutorView(BlogDetailView):
    template_name = "djcms_blog/author.html"
    slug_field = "slug"
    slug_url_kwarg = "author_slug"
    model = Author

    def get_context_data(self, **kwargs):
        context = super(AutorView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        self.set_language()
        self.object = self.get_object()
        lang_object = self.object.get_language_object(self.language)
        self.object.bio = lang_object.bio
        self.object.get_posts = self.object.get_posts()
        for post in self.object.get_posts:
            post.title = post.language_object(self.language).title
            post.description = post.language_object(self.language).description
            post.published_date = post.language_object(self.language).published_date
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class PostView(BlogDetailView):
    template_name = "djcms_blog/post.html"
    slug_field = "slug"
    slug_url_kwarg = "post_slug"
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        self.set_language()
        self.object = self.get_object()
        if not self.object.is_published:
            raise Http404("Not found")

        lang_object = self.object.language_object(self.language)
        self.object.title_id = lang_object.id
        self.object.title = lang_object.title
        self.object.body = lang_object.body
        self.object.publisher_public = lang_object.publisher_public
        self.object.published = lang_object.published
        self.object.publisher_draft = lang_object.publisher_draft
        self.object.published_date = lang_object.published_date
        self.object.meta_title = lang_object.meta_title
        self.object.meta_description = lang_object.meta_description
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class PostDraftView(PostView):
    def get_object(self, queryset=None):

        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug, "publisher_is_draft": True})

        if pk is None and slug is None:
            raise AttributeError(
                "Generic detail view %s must be called with "
                "either an object pk or a slug." % self.__class__.__name__
            )
        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj
