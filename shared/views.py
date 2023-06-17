from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
# Create your views here.
from django.contrib import auth

from shared.forms import ProfileRegisterForm, UserRegisterForm
from shared.models import Profile


class LoginException(BaseException):
    message = None

    def __init__(self, message):
        # override public fields
        self.message = message

    def getMessage(self):
        return self.message


def autenticate(username, password):
    if not username:
        raise LoginException('You did not provide the username!')
    if not password:
        raise LoginException('You did not provide a password!')
    user = auth.authenticate(username=username, password=password)
    if user is None:
        raise LoginException('Username and/or password are incorrect.')

    # if not user.check_password(password):
    #    raise LoginException('Incorrect password for this user\'s email!')
    return user


def login_view(request):
    template_name = 'registration/login.html'
    context = {}
    if request.POST:
        try:
            user = autenticate(request.POST['username'], request.POST['password'])
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("user_dashboard")
        except LoginException as error:
            context.update({"error": error.getMessage()})
        except:
            context.update({"error": "Unexpected error. Please contact admin!"})
    return render(request, template_name, context)


def register_view(request):
    template_name = 'registration/register.html'
    user_form = UserRegisterForm(request.POST or None)
    profile_form = ProfileRegisterForm()
    if user_form.is_valid():
        submit_is_ok, user = user_form.submit()
        if submit_is_ok:
            profile_form = ProfileRegisterForm(request.POST or None, instance=user.profile)
            if profile_form.is_valid():
                if profile_form.submit():
                    auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return redirect('user_contests_home')

    context = {
        "userForm": user_form,
        "profileForm": profile_form
    }
    return render(request, template_name, context)
