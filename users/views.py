# Cannot get profile to work, commenting out code for now

"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .forms import CustomSignupForm

@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = CustomSignupForm(request.POST, instance=request.user.profile)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('settings:profile')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user.profile)
    return render(request, 'users/profile.html', {
        'user_form': user_form
    })
"""