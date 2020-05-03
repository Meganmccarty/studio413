from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post, Comment, Subscriber
from .forms import PostForm, CommentForm, SubscriberForm, ContactForm
from .etsy import etsy_data
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

### These views are public (do NOT require admin log in) --->

### Blog Page (Post List)
def post_list(request):
    post_list = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    paginator = Paginator(post_list, 10)

    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post_list.html', {'post_list': post_list, 'page' : page, 'posts' : posts })

### Detailed Post
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(approved_comment=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form})

### Home Page
def home(request):
    return render(request, 'blog/home.html')

### Products Page
def products(request):
    parsed_data = []
    etsy_results = etsy_data['results']

    for results in etsy_results:
        result_data = {}
        result_data['title'] = results['title']
        result_data['price'] = results['price']
        result_data['url'] = results['url']
        result_data['views'] = results['views']
        result_data['likes'] = results['num_favorers']
        result_data['image'] = results['Images'][0]['url_570xN']
        result_data['digital'] = results['is_digital']
        parsed_data.append(result_data)

    return render(request, 'blog/products.html', {'data' : parsed_data})

### Contact Page
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # send email code goes here
            sender_name = form.cleaned_data['name']
            sender_email = form.cleaned_data['email']

            message = "{0} has sent you a new message:\n\n{1}".format(sender_name, form.cleaned_data['message'])
            send_mail('New Enquiry', message, sender_email, [settings.STUDIO413_EMAIL])
            return render(request, 'blog/success.html')
    else:
        form = ContactForm()

    return render(request, 'blog/contact.html', {'form': form})

### New Subscriber Page
# Helper Functions

def random_digits():
    return "%0.12d" % random.randint(0, 999999999999)

@csrf_exempt
def new(request):
    if request.method == 'POST':
        sub = Subscriber(first_name=request.POST['first_name'],
                            last_name=request.POST['last_name'],
                            email=request.POST['email'],
                            conf_num=random_digits())
        sub.save()
        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=sub.email,
            subject='Welcome to the Studio413 Newsletter!',
            html_content='<p>Hello {}!</p> <br> <p>Thank you for signing up for the Studio413 newsletter! \
                I\'m looking forward to sharing exclusive creative art content with you here!</p> \
                <p>Before you can receive your exclusive member goodies, please \
                <a href="{}?email={}&conf_num={}"> click here to \
                confirm your registration</a>.</p>'.format(sub.first_name,
                                                    request.build_absolute_uri('/confirm/'),
                                                    sub.email,
                                                    sub.conf_num))
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return render(request, 'blog/new_subscriber.html', {'email': sub.email, 'action': 'added', 'form': SubscriberForm()})
    else:
        return render(request, 'blog/new_subscriber.html', {'form': SubscriberForm()})

def confirm(request):
    sub = Subscriber.objects.get(email=request.GET['email'])
    if sub.conf_num == request.GET['conf_num']:
        sub.confirmed = True
        sub.save()
        return render(request, 'blog/new_subscriber.html', {'email': sub.email, 'action': 'confirmed'})
    else:
        return render(request, 'blog/new_subscriber.html', {'email': sub.email, 'action': 'denied'})

def delete(request):
    sub = Subscriber.objects.get(email=request.GET['email'])
    if sub.conf_num == request.GET['conf_num']:
        sub.delete()
        return render(request, 'blog/new_subscriber.html', {'email': sub.email, 'action': 'unsubscribed'})
    else:
        return render(request, 'blog/new_subscriber.html', {'email': sub.email, 'action': 'denied'})

### These views are private (REQUIRE admin log in) --->

### New Post
@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

### Edit Post
@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

### Drafts List Page
@login_required
def post_draft_list(request):
    post_list = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    paginator = Paginator(post_list, 3)

    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post_list.html', {'post_list': post_list, 'page' : page, 'posts' : posts })
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

### Publish Draft Post
@login_required
def post_publish(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.publish()
    return redirect('post_detail', slug=slug)

### Delete Post
@login_required
def post_remove(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.delete()
    return redirect('post_list')
