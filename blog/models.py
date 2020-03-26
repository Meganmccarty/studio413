import base64
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(null=True, blank=True)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def approved_comments(self):
        return self.comments.filter(approved_comment=True)

    def save(self, *args, **kwargs):
        slug = slugify(self.title)
        self.slug = slug
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text

class Subscriber(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    conf_num = models.CharField(max_length=15)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.email + " (" + ("not " if not self.confirmed else "") + "confirmed)"

class Newsletter(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)
    subject = models.CharField(max_length=150)
    contents = models.FileField(upload_to='uploaded_newsletters/')
    attachment = models.FileField(upload_to='email_attachments/', default='', null=True, blank=True)

    def __str__(self):
        return self.subject + " " + self.created_at.strftime("%B %d, %Y")

    def send(self, request):
        contents = self.contents.read().decode('utf-8')
        subscribers = Subscriber.objects.filter(confirmed=True)
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        for sub in subscribers:
            message = Mail(
                    from_email=settings.FROM_EMAIL,
                    to_emails=sub.email,
                    subject=self.subject,
                    html_content=contents + (
                        '<br><center>If you no longer wish to receive our newsletters, you can ' \
                        '<a href="{}/?email={}&conf_num={}">unsubscribe</a></center>.').format(
                            request.build_absolute_uri('/delete/'),
                            sub.email,
                            sub.conf_num))

            with open(self.attachment.path, 'rb') as f:
                data = f.read()
                f.close()
            encoded_file = base64.b64encode(data).decode()

            attachedFile = Attachment(
                FileContent(encoded_file),
                FileName(self.attachment.path),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            message.attachment = attachedFile

            sg.send(message)