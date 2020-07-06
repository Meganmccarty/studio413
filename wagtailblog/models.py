from django.db import models
from django.dispatch import receiver
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.conf import settings
from django.core.mail import send_mail

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.search import index
from wagtail.core.signals import page_published

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]

class BlogIndexPage(Page):
    template = "wagtailblog/blog_index_page.html"

    def get_context(self, request, *args, **kwargs):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(BlogIndexPage, self).get_context(request, *args, **kwargs)
        blogpages = BlogPage.objects.live().public().order_by('-first_published_at')
        paginator = Paginator(blogpages, 5)
        page = request.GET.get("page")
        try:
            blogpages = paginator.page(page)
        except PageNotAnInteger:
            blogpages = paginator.page(1)
        except EmptyPage:
            blogpages = paginator.page(paginator.num_pages)

        context["blogpages"] = blogpages

        return context

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

class BlogPage(Page):
    date = models.DateField("Post date")
    author = models.CharField(max_length=250, default='', null=True, blank=True)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('author'),
            FieldPanel('date'),
            FieldPanel('tags'),
        ], heading="Blog information"),
        FieldPanel('body'),
    ]

    def send(self, request):
        subscribers = Subscriber.objects.filter(confirmed=True)
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        for sub in subscribers:
            message = Mail(
                from_email=settings.FROM_EMAIL,
                to_emails=sub.email,
                subject="New blog post on Studio413!",
                html_content=(
                    '<div style="background-color:rgb(0,40,110);border:10px solid rgb(0,40,110);border-radius:10px">' \
                    '<div style="background-color:rgb(193,222,227);border:10px solid rgb(193,222,227);border-radius:10px">' \
                    '<div style="background-color:white;border-radius:10px">' \
                    '<center><h3>Studio413 has published a new blog post!</h3></center>'\
                    '<br>' \
                    '<span style="margin-left:10px">Click the following link to read the new post:</span>' \
                    '<br>' \
                    '<span style="margin-left:10px"><a href="{}/{}/">{}</a></span>'\
                    '<br>' \
                    '<span style="margin-left:10px">Or, you can copy and paste the following url into your browser:</span>' \
                    '<br>' \
                    '<span style="margin-left:10px">{}/{}</span>'\
                    '<br>' \
                    '<hr><center>If you no longer wish to receive our blog updates, you can ' \
                    '<a href="{}/?email={}&conf_num={}">unsubscribe</a>.</center><br></div></div></div>').format(
                        request.build_absolute_uri('/blog'),
                        self.slug,
                        self.title,
                        request.build_absolute_uri('/blog'),
                        self.slug,
                        request.build_absolute_uri('/delete'),
                        sub.email,
                        sub.conf_num
                    )
                )
            sg.send(message)

class BlogTagIndexPage(Page):
    pass

    def get_context(self, request):
        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context

class Subscriber(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    conf_num = models.CharField(max_length=15)
    confirmed = models.BooleanField(default=False)

    @receiver(models.signals.post_save, sender='wagtailblog.Subscriber')
    def execute_after_save(sender, instance, created, *args, **kwargs):
        if created:
            email_message = 'You have a new subscriber for your blog! ' \
                'To see who it is, click the following link:\n\n' \
                'https://www.zenstudio413.com/admin/blog/subscriber/ ' \
                '\n\nDo not respond to this email address. If you wish to reach the webmaster, ' \
                'forward this email, along with your message, to megan_mccarty@hotmail.com'
            send_mail(
                subject='New Subscriber',
                message=email_message,
                from_email='admin@zenstudio413.com',
                recipient_list=[settings.STUDIO413_EMAIL]
            )

    def __str__(self):
        return self.email + " (" + ("not " if not self.confirmed else "") + "confirmed)"