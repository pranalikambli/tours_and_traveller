from .user.registration_form import UserRegistrationForm, UserProfileForm, LoginForm
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
import datetime


class UserFormsMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if('user' not in request.session and request.is_ajax() is False):
            request.user_form =  UserRegistrationForm(None)
            request.profile_form = UserProfileForm(None)
            request.login_form = LoginForm(request.POST or None)


class MultipleProxyForbiddenMiddleware(MiddlewareMixin):
    template_name = '403.html'

    def process_request(self, request):
        if 'user' in request.session.keys():
            # User Logged in
            if request.path == reverse('forgot-password'):
                return render(request, self.template_name, status=403)
            elif request.path == reverse('reset-password'):
                return render(request, self.template_name, status=403)
            elif request.path == reverse('sign-up'):
                return render(request, self.template_name, status=403)
            elif request.path == reverse('user-sign-in'):
                return render(request, self.template_name, status=403)


"""
    Author Name : Pranali Kambli
    Date : 3/09/2019
    Purpose : This class will redirect user on login page and remove the session.(Session time out) 

"""


class SessionExpiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'user' in request.session.keys():
            login_time_str = request.session['user']['login_time']
            login_time = login_time_str[:19]
            login_time_obj = datetime.datetime.strptime(login_time, '%Y-%m-%d %H:%M:%S')
            now = str(datetime.datetime.now(tz=timezone.utc))
            now_str_time = now[:19]
            now_date_obj = datetime.datetime.strptime(now_str_time, '%Y-%m-%d %H:%M:%S')
            diff = now_date_obj - login_time_obj
            diff_minutes = diff.seconds / 60
            if diff_minutes > int(settings.SESSION_LOGOUT_TIME):
                for k in list(request.session.keys()):
                    del request.session[k]
                messages.warning(request, 'Your session expired. Please login again!')
                return redirect('index')
        return None