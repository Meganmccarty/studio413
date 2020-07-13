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

from django_comments_xtd.models import XtdComment
from django_comments.moderation import CommentModerator
from django_comments_xtd.moderation import moderator, SpamModerator
from wagtailblog.badwords import badwords

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]

class MemberOnlyPage(Page):
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

    def get_absolute_url(self):
        return 'http://127.0.0.1:8000' + self.url
    
    def get_context(self, request, *args, **kwargs):
        context = super(BlogPage, self).get_context(request, *args, **kwargs)
        context['COMMENTS_APP'] = COMMENTS_APP
        return context

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
                    '<span style="margin-left:10px"><a href="http://127.0.0.1:8000/blog/{}/">{}</a></span>'\
                    '<br>' \
                    '<span style="margin-left:10px">Or, you can copy and paste the following url into your browser:</span>' \
                    '<br>' \
                    '<span style="margin-left:10px">http://127.0.0.1:8000/blog/{}</span>'\
                    '<br>' \
                    '<hr><center>If you no longer wish to receive our blog updates, you can ' \
                    '<a href="http://127.0.0.1:8000/delete/?email={}&conf_num={}">unsubscribe</a>.</center><br></div></div></div>').format(
                        self.slug,
                        self.title,
                        self.slug,
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

COMMENTS_APP = getattr(settings, 'COMMENTS_APP', None)

class Comments(XtdComment):
    XtdComment.panels = [
        MultiFieldPanel([
            FieldPanel('user', heading='Username'),
            FieldPanel('user_name', help_text='User\'s first and last name'),
            FieldPanel('user_email'),
            FieldPanel('user_url'),
        ], heading='User information'),
        FieldPanel('submit_date'),
        FieldPanel('comment'),
        MultiFieldPanel([
            FieldPanel('is_public'),
            FieldPanel('is_removed'),
        ], heading='Moderation'),
    ]

class PostCommentModerator(CommentModerator):
    email_notification = True

    def moderate(self, comment, content_object, request):
        # Make a dictionary where the keys are the words of the message and
        # the values are their relative position in the message.
        def clean(word):
            ret = word
            if word.startswith('.') or word.startswith(','):
                ret = word[1:]
            if word.endswith('.') or word.endswith(','):
                ret = word[:-1]
            return ret

        lowcase_comment = comment.comment.lower()
        msg = dict([(clean(w), i)
                    for i, w in enumerate(lowcase_comment.split())])
        for badword in badwords:
            if isinstance(badword, str):
                if lowcase_comment.find(badword) > -1:
                    return True
            else:
                lastindex = -1
                for subword in badword:
                    if subword in msg:
                        if lastindex > -1:
                            if msg[subword] == (lastindex + 1):
                                lastindex = msg[subword]
                        else:
                            lastindex = msg[subword]
                    else:
                        break
                if msg.get(badword[-1]) and msg[badword[-1]] == lastindex:
                    return True
        return super(PostCommentModerator, self).moderate(comment,
                                                          content_object,
                                                          request)

moderator.register(BlogPage, PostCommentModerator)