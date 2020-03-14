from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post, Comment, Subscriber
from .forms import PostForm, CommentForm, SubscriberForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.conf import settings
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

### These views are public (do NOT require admin log in) --->

### Home Page (Post List)
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

### About Page
def about(request):
    return render(request, 'blog/about.html')

### Products Page
def products(request):
    return render(request, 'blog/products.html')

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
            html_content='Thank you for signing up for the Studio413 newsletter! \
                Before you can receive your exclusive member goodies, please \
                <a href="{}/confirm/?email={}&conf_num={}"> click here to \
                confirm your registration</a>.'.format(request.build_absolute_uri('/confirm/'),
                                                    sub.email,
                                                    sub.conf_num))
        sg = SendGridAPIClient('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')
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
