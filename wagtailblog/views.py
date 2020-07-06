from django.shortcuts import render
from .models import Subscriber
from .forms import SubscriberForm, ContactForm
from .etsy import etsy_data
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

### Products Page
def products(request):
    parsed_data = []
    etsy_results = etsy_data['results']

    for results in etsy_results:
        result_data = {}
        result_data['id'] = results['listing_id']
        result_data['image'] = results['Images'][0]['url_570xN']
        parsed_data.append(result_data)

    return render(request, 'blog/products.html', {'data' : parsed_data})

### Therapeutic Art Pages Subpage
def art_pages(request):
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

    return render(request, 'blog/art_pages.html', {'data' : parsed_data})

### Art for Sale Subpage
def art_for_sale(request):
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

    return render(request, 'blog/art_for_sale.html', {'data' : parsed_data})

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
            subject='Welcome to Studio413!',
            html_content='<p>Hello {}!</p> <br> <p>Thank you for subscribing to Studio413! \
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