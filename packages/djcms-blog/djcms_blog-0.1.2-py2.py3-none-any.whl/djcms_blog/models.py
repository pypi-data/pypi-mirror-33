from django.db import models
from django.contrib.auth.models import User
from simplemde.fields import SimpleMDEField
from datetime import datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone

from .utils import expire_page


def expire_blog_post(post):
    post_url = reverse(
        "post-detail",
        kwargs={"blog_slug": post.post.blog.slug, "post_slug": post.post.slug},
    )
    expire_page(post_url)
    blog_url = reverse("blog-main", kwargs={"blog_slug": post.post.blog.slug})
    expire_page(blog_url)
    author_url = reverse("author-main", kwargs={"author_slug": post.post.author.slug})
    expire_page(author_url)


class Author(models.Model):
    user = models.OneToOneField(User, related_name="author_profile")
    cover = models.ImageField(upload_to="author_cover")
    image = models.ImageField(upload_to="image")
    slug = models.CharField(max_length=140)
    location = models.CharField(max_length=100)
    website = models.URLField(max_length=100)
    facebook_profile = models.URLField(max_length=100)
    twitter_profile = models.URLField(max_length=100)
    block_header = SimpleMDEField(max_length=10000, blank=True, null=True)
    block_footer = SimpleMDEField(max_length=10000, blank=True, null=True)

    def __str__(self):
        return self.user.email

    def get_language_object(self, language):
        language_object = AuthorBio.objects.filter(
            author=self, language=language
        ).first()
        if language_object:
            return language_object

    def has_language(self, language):
        if AuthorBio.objects.filter(author=self, language=language).first():
            return True
        return False

    def get_posts(self):
        return Post.objects.author_posts(author=self)

    def get_post_count(self):
        return Post.objects.author_posts(author=self).count()

    def get_name(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)


class AuthorBio(models.Model):
    author = models.ForeignKey(Author, db_index=True)
    bio = SimpleMDEField(max_length=255)
    language = models.CharField(
        max_length=15, db_index=True, choices=settings.LANGUAGES
    )

    def __str__(self):
        return "{} {}".format(self.author, self.language)

    def get_posts(self):
        return Post.objects.blog_posts(blog=self)


class Blog(models.Model):
    title = models.CharField(max_length=140)
    slug = models.CharField(max_length=140, db_index=True)
    cover = models.ImageField(upload_to="blog_cover")
    block_header = SimpleMDEField(max_length=10000, blank=True, null=True)
    block_footer = SimpleMDEField(max_length=10000, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_posts(self):
        return Post.objects.blog_posts(blog=self)

    def has_language(self, language):
        if BlogTitle.objects.filter(blog=self, language=language).first():
            return True
        return False

    def get_language_object(self, language):
        language_object = BlogTitle.objects.filter(blog=self, language=language).first()
        if language_object:
            return language_object


class BlogTitle(models.Model):
    blog = models.ForeignKey(Blog, db_index=True)
    language = models.CharField(
        max_length=15, db_index=True, choices=settings.LANGUAGES
    )
    title = models.CharField(max_length=140)
    description = SimpleMDEField(max_length=255)
    meta_title = SimpleMDEField(max_length=70, blank=True, null=True)
    meta_description = SimpleMDEField(max_length=156, blank=True, null=True)

    class Meta:
        unique_together = ("blog", "language")

    def __str__(self):
        return self.title


class Tag(models.Model):
    COLOR_CHOICES = (
        ("red", "red"),
        ("orange", "orange"),
        ("yellow", "yellow"),
        ("olive", "olive"),
        ("green", "green"),
        ("teal", "teal"),
        ("blue", "blue"),
        ("violet", "violet"),
        ("purple", "purple"),
        ("pink", "pink"),
        ("brown", "brown"),
        ("grey", "grey"),
        ("black", "black"),
    )
    blog = models.ForeignKey(Blog, db_index=True)
    cover = models.ImageField(upload_to="tag_cover")
    name = models.CharField(max_length=140)
    slug = models.CharField(max_length=140)
    color = models.CharField(max_length=14, choices=COLOR_CHOICES)
    meta_title = SimpleMDEField(max_length=70, blank=True, null=True)
    meta_description = SimpleMDEField(max_length=156, blank=True, null=True)

    def __str__(self):
        return self.name

    def has_language(self, language):
        if TagTitle.objects.filter(tag=self, language=language).first():
            return True
        return False

    def get_posts(self):
        return Post.objects.published_tag(tag=self)

    def get_post_count(self):
        return Post.objects.published_tag(tag=self).count()

    def get_language_object(self, language):
        language_object = TagTitle.objects.filter(tag=self, language=language).first()
        if language_object:
            return language_object


class TagTitle(models.Model):
    tag = models.ForeignKey(Tag, db_index=True)
    language = models.CharField(
        max_length=15, db_index=True, choices=settings.LANGUAGES
    )
    name = models.CharField(max_length=140)
    description = SimpleMDEField(max_length=200)
    meta_title = SimpleMDEField(max_length=70, blank=True, null=True)
    meta_description = SimpleMDEField(max_length=156, blank=True, null=True)

    class Meta:
        unique_together = ("tag", "language")

    def __str__(self):
        return self.name


class PostManager(models.Manager):
    def published(self):
        posts = PostTitle.objects.filter(
            published=True, publisher_is_draft=False
        ).values_list("post", flat=True)
        return Post.objects.filter(id__in=posts)

    def published_tag(self, tag):
        return self.published().filter(tag__in=[tag])

    def blog_posts(self, blog):
        return self.published().filter(blog=blog)

    def author_posts(self, author):
        return self.published().filter(author=author)


class Post(models.Model):
    blog = models.ForeignKey(Blog, db_index=True)
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=140)
    cover = models.ImageField(upload_to="post_cover", blank=True, null=True)
    author = models.ForeignKey(Author, db_index=True)
    tag = models.ManyToManyField(Tag)

    objects = PostManager()

    def __str__(self):
        return self.title

    def get_tags(self):
        return self.tag.all()

    def language_object(self, language):
        language_object = PostTitle.objects.filter(
            post=self, language=language, publisher_is_draft=False, published=True
        ).first()
        if language_object:
            return language_object
        return PostTitle.objects.filter(
            post=self, publisher_is_draft=False, published=True
        ).first()

    def get_language_object(self, language):
        language_object = PostTitle.objects.filter(
            post=self, language=language, publisher_is_draft=True
        ).first()
        if language_object:
            return language_object

    def has_language(self, language):
        if PostTitle.objects.filter(post=self, language=language).first():
            return True
        return False

    def is_published(self):
        if PostTitle.objects.filter(
            post=self, publisher_is_draft=False, published=True
        ).first():
            return True
        return False


class PostTitle(models.Model):
    post = models.ForeignKey(Post, db_index=True)
    title = models.CharField(max_length=255)
    language = models.CharField(
        max_length=15, db_index=True, choices=settings.LANGUAGES
    )
    description = SimpleMDEField(max_length=80000)
    body = SimpleMDEField(max_length=80000)
    meta_title = SimpleMDEField(max_length=70, blank=True, null=True)
    meta_description = SimpleMDEField(max_length=156, blank=True, null=True)
    published = models.BooleanField(blank=True, default=False)
    publisher_is_draft = models.BooleanField(
        default=True, editable=False, db_index=True
    )
    publisher_public = models.OneToOneField(
        "self",
        on_delete=models.CASCADE,
        related_name="publisher_draft",
        null=True,
        editable=False,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("post", "language", "publisher_is_draft")

    def save(self, *args, **kwargs):
        print("Values to save", args, kwargs)
        super(PostTitle, self).save(*args, **kwargs)

    def edited(self):
        if self.publisher_public:
            if all(
                (
                    self.publisher_public.post == self.post,
                    self.publisher_public.title == self.title,
                    self.publisher_public.language == self.language,
                    self.publisher_public.description == self.description,
                    self.publisher_public.body == self.body,
                    self.publisher_public.meta_title == self.meta_title,
                    self.publisher_public.meta_description == self.meta_description,
                )
            ):
                return False
            return True
        return False

    def create_public_post(self):
        publisher_public = PostTitle(
            post=self.post,
            title=self.title,
            language=self.language,
            description=self.description,
            body=self.body,
            meta_title=self.meta_title,
            meta_description=self.meta_description,
            publisher_is_draft=False,
            published=True,
            published_date=datetime.now(tz=timezone.utc),
        )
        publisher_public.save()
        self.publisher_public = publisher_public
        self.published = True
        self.publisher_edited = False
        self.published_date = datetime.now(tz=timezone.utc)
        self.save()

    def publish(self):
        if self.publisher_public is None:
            self.create_public_post()
            expire_blog_post(self)
            return True
        else:
            if self.edited():
                publisher_public = self.publisher_public
                self.publisher_public = None
                self.create_public_post()
                expire_blog_post(self)
                publisher_public.delete()
                return True
        return False

    def unpublish(self):
        publisher_public = self.publisher_public
        self.publisher_public = None
        publisher_public.delete()
        self.published = False
        self.published_date = None
        expire_blog_post(self)
        self.save()
