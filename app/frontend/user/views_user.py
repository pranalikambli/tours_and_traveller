from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.db.models import Sum
from django.utils import timezone
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.conf import settings

import datetime
import json

from .registration_form import UserRegistrationForm, UserProfileForm, ForgotPasswordForm, ResetPasswordForm, LoginForm, \
    UpdateUserProfileForm, UpdateUserRegistrationForm, ChangePasswordForm
from .services import get_user_by_token, send_user_mail, get_city_list, get_city_id_list, list_comapre, \
    convert_datetime_to_int, get_client_ip, get_roleid
from .token import account_activation_token
from .models_user import user, guide_profile, guide_rating, guide_city, city, user_profile, user_login
from frontend.role_management.models_user_permissions import role_group_permissions, group_permissions
from frontend.message_board.models_message import predefine_messages
from frontend.search.services import remove_non_ascii


# Create your views here.
def sign_up(request):
    user_form = UserRegistrationForm(request.POST or None, request.FILES)
    profile_form = UserProfileForm(request.POST or None)

    user_valid = user_form.is_valid()
    profile_valid = profile_form.is_valid()

    to_email = user_form.cleaned_data.get('email')
    message = ''
    success = 0
    if user_valid and profile_valid:
        is_guide = profile_form.cleaned_data['is_guide']
        hashed_password = user_form.get_encrypyt_password()
        user_obj = user_form.save(commit=False)
        user_obj.role_id = get_roleid('guide') if is_guide == 1 else get_roleid('customer')
        user_obj.password = hashed_password
        user_obj.active = 0
        user_obj.save()
        profile_form.instance.user_id = user_obj.user_id
        profile_form.save()
        if is_guide == 1:
            city_list = profile_form.cleaned_data.get('city_hidden')
            cities_list = city_list.split(', ')
            guide_profile_obj = guide_profile.objects.create(user_id=user_obj.pk, is_verified=1)
            for city_name in cities_list:
                city_obj = city.objects.filter(city=city_name).first()
                if city_obj:
                    guide_city.objects.create(guide_id=guide_profile_obj.user_id, city_id=city_obj.city_id)
        success = 1
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
        current_site = get_current_site(request)
        mail_subject = 'Activate your account.'
        email_content = render_to_string('user/acc_active_email.html', {
            'user': user_obj,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user_obj.pk)),
            'token': account_activation_token.make_token(user_obj),
        })
        email = EmailMessage(
            mail_subject, email_content, to=[to_email]
        )
        email.send()
        message = 'Please confirm your email address to complete the registration'

    # message='User Account Successfully created.'

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'success': success,
        'message': message
    }

    request.user_form = user_form
    request.profile_form = profile_form

    template = 'user/registration_form_fields.html' if request.is_ajax() else "user/sign-up.html"

    return render(request, template, context)


def forgot_password(request):
    form = ForgotPasswordForm(request.POST or None)
    message = ''
    error = 0

    if form.is_valid():

        if form.email_exists():
            # Account found
            message += form.user_id
            query_string = form.get_reset_token_params()

            send_user_mail('Password Reset Link',
                           'Your Reset link ' + request.build_absolute_uri('/reset-password') + '?' + query_string,
                           'support@triplani.com',
                           [form.cleaned_data.get('email')],
                           fail_silently=False)

            message = _(
                "An email with the password reset token will be sent to entered email, if we find a registered active account. Reset token expires in an hour.")
            form = ForgotPasswordForm()

    context = {
        'form': form,
        'error': error,
        'message': message
    }

    return render(request, 'user/forgot_password.html', context)


def reset_password(request):
    form = ForgotPasswordForm(request.POST or None)
    reset_form = ResetPasswordForm(request.POST or None)
    message = ''
    error = 2

    id = request.GET.get('id', '')
    token = request.GET.get('token', '')
    success = request.GET.get('success', '')

    if (success != '1'):
        try:
            user_id = form.get_decrypted_user_id(id)
            token = form.get_decrypted_user_id(token)
            user_data = get_user_by_token(user_id, token)
            if 'user_id' in user_data:
                error = 0
        except Exception as e:
            message = _("Reset link is expired or not valid.")

        if reset_form.is_valid():
            update_status = reset_form.update_password(user_data['user_id'], user_data['token_id'])
            if (update_status):
                message = _("Password successfully updated.")
                full_redirect_url = reverse('reset-password') + '?success=1';
                return HttpResponseRedirect(full_redirect_url)
            else:
                error = 1
                message = _("Please try to reset password again or click on forgot password.")
    else:
        error = 0
        message = _("Password successfully updated.")

    context = {
        'form': reset_form,
        'error': error,
        'message': message,
        'success': success
    }

    if (error == 2):
        # 2 page not found
        return HttpResponseNotFound(message)

    return render(request, 'user/reset_password.html', context)


def user_sign_in(request):
    if request.is_ajax() is False:
        return HttpResponseNotFound('Invalid Request')

    login_form = LoginForm(request.POST or None)
    message = ''
    error = 1

    if login_form.is_valid():
        user_obj = login_form.get_user()
        if user_obj == None:
            message = _("Sorry, First Activate your account")
            error = 1
        elif user_obj.count() > 0:
            user_json = model_to_dict(user_obj[0])
            role_group_permissions_obj = json.dumps(
                role_group_permissions.objects.filter(role_id=user_json['role_id']).values('group_permission')[0],
                sort_keys=True, default=str)
            role_group_permissions_dict = json.loads(role_group_permissions_obj)
            role_group_permissions_dict = json.loads(role_group_permissions_dict['group_permission'])
            login_time = convert_datetime_to_int(datetime.datetime.now(tz=timezone.utc))
            user_json['full_name'] = user_json['first_name'] + " " + user_json['last_name']
            user_json['profile_picture'] = json.dumps(str(user_json['profile_picture']))
            user_json['login_time'] = str(datetime.datetime.now(tz=timezone.utc))
            user_json['role_group_permissions'] = role_group_permissions_dict
            request.session['user'] = user_json
            error = 0
            request.session['last_activity'] = str(datetime.datetime.now())
            user_login.objects.create(user_id=user_json['user_id'], login_ip=get_client_ip(request),
                                                    login_time=str(login_time))
        else:
            message = _("Sorry, that's not a valid email or password")
            error = 1

    context = {
        'login_form': login_form,
        'message': message,
        'error': error
    }

    request.login_form = login_form
    if request.is_ajax():
        json_data = {'html': render_to_string('user/user_sign_in.html', context, request), 'error': error}
        # context_instance = RequestContext(request)
        return JsonResponse(json_data)

    return render(request, 'user/user_sign_in.html', context)


def user_sign_out(request):
    for k in list(request.session.keys()):
        del request.session[k]
    return redirect('index')


"""
    Author Name : Pranali Kambli
    Date : 31/08/2019
    Purpose : This class will return the guide details by user_id.
"""


class GuideProfile(View):
    template_name = 'user/guide_profile.html'

    def get(self, request, guide_id):
        guide_details = guide_profile.objects.filter(user_id=guide_id, is_verified=True).first()
        get_msg_list = predefine_messages.objects.all()
        return render(request, self.template_name, {'guide_details': guide_details, 'msg_list': get_msg_list})


# get sms message request
def sendPostRequest(reqUrl, apiKey, secretKey, useType, phoneNo, senderId, textMessage):
    req_params = {
        'apikey': apiKey,
        'secret': secretKey,
        'usetype': useType,
        'phone': phoneNo,
        'message': textMessage,
        'senderid': senderId
    }
    # return requests.post(reqUrl, req_params)
    pass


"""
    Author Name : Pranali Kambli
    Date : 3/09/2019
    Purpose : This function will return text message on selected user's number.
"""


def send_sms(request):
    user_number = request.POST.get('user_number')
    message = request.POST.get('message')
    url = 'https://www.way2sms.com/api/v1/sendCampaign'
    response = sendPostRequest(url, 'provided-api-key', 'provided-secret', 'prod/stage', user_number,
                               'active-sender-id', message)
    print(response.text)


"""
    Author Name : Pranali Kambli
    Date : 04/09/2019
    Purpose : Add the ratings to guide.
"""


class GuideRating(View):
    def get(self, request):
        try:
            if 'user' in request.session.keys():
                logged_in_user_id = request.session.get('user')['user_id']
                guide_id = request.GET.get('guideId')
                rating_val = request.GET.get('ratingValue')
                unq_id = str(guide_id) + ':' + str(logged_in_user_id)
                check_user_exist = guide_rating.objects.filter(guide_id=guide_id, user_id=logged_in_user_id).first()
                if check_user_exist:
                    guide_rating.objects.filter(guide_id=guide_id, user_id=logged_in_user_id).update(
                        rating=rating_val, last_update=str(datetime.datetime.now(tz=timezone.utc)))
                else:
                    guide_rating.objects.create(rating_id=1, unq_id=unq_id, guide_id=guide_id,
                                                user_id=logged_in_user_id, rating=rating_val)

                guide_rating_count_obj = guide_rating.objects.filter(guide_id=guide_id).all()
                sum_of_guide_rating = guide_rating_count_obj.aggregate(Sum('rating'))['rating__sum']
                # add the count of ratings given by users
                if guide_rating_count_obj:
                    guide_profile.objects.filter(user_id=guide_id).update(ratings=int(sum_of_guide_rating),
                                                                          total_ratings=int(
                                                                              guide_rating_count_obj.count()))

                return JsonResponse({'msg': 'success'})
        except Exception as e:
            return JsonResponse({'msg': e})


"""
    Author Name : Pranali Kambli
    Date : 04/09/2019
    Purpose : Activate user account.
"""


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user_obj = user.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user_obj = None

    if user_obj is not None and account_activation_token.check_token(user_obj, token):
        user_obj.active = True
        user_obj.save()
        message = _("Your account has successfully created!")
        return render(request, "user/account_activation.html", {'message': message, 'error': 0})
    else:
        message = _('Activation link is invalid!')
        return render(request, "user/account_activation.html", {'message': message, 'error': 1})


"""
    Author Name : Pranali Kambli
    Date : 16/09/2019
    Purpose : Return city list from city table.
"""


def city_autocomplete(request):
    search_filter = request.POST.get('city', '')
    search_filter_text = search_filter.strip()
    data = {}

    result = get_city_list(search_filter_text)
    for each in result:
        data[each[0]] = remove_non_ascii(each[1])
    return JsonResponse(data)


"""
    Author Name : Pranali Kambli
    Date : 19/09/2019
    Purpose : Update User.
"""


class UpdateUser(View):
    user_form = UpdateUserRegistrationForm()
    profile_form = UpdateUserProfileForm()

    def get(self, request, pk):

        user_obj = get_object_or_404(user, pk=pk)
        profile_obj = get_object_or_404(user_profile, pk=pk)

        user_form = UpdateUserRegistrationForm(request.POST or None, instance=user_obj)
        profile_form = UpdateUserProfileForm(request.POST or None, instance=profile_obj)
        profile_form.fields['userid'].initial = pk
        try:
            is_guide = guide_profile.objects.get(user_id=pk)
        except Exception as e:
            is_guide = None
        if is_guide:
            profile_form.fields['is_guide'].initial = 1
            guide_city_list = guide_city.objects.filter(guide_id=pk).values_list('city_id', flat=True)
            guide_city_list = city.objects.filter(city_id__in=guide_city_list).values_list('city', flat=True)
            city_list = ','.join(map(str, guide_city_list))
            profile_form.fields['city_hidden'].initial = city_list
        else:
            profile_form.fields['is_guide'].initial = 0
        context = {'user_form': user_form, 'profile_form': profile_form, 'JS_CSS_VERSION': settings.JS_CSS_VERSION}
        request.user_form = user_form
        request.profile_form = profile_form
        template = "user/update_user.html"
        return render(request, template, context)

    def post(self, request, pk):
        message = ''
        success = 0

        user_form = UpdateUserRegistrationForm(request.POST)
        profile_form = UpdateUserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            try:
                is_guide = user.objects.filter(user_id=profile_form.cleaned_data.get('userid'), role_id=2).first()
            except Exception as e:
                is_guide = None
            # update user
            user.objects.filter(user_id=pk).update(first_name=user_form.cleaned_data.get('first_name'),
                                                   last_name=user_form.cleaned_data.get('last_name'),
                                                   email=user_form.cleaned_data.get('email'),
                                                   sex=user_form.cleaned_data.get('sex'))

            # update user_profile
            user_profile.objects.filter(user_id=pk).update(phone=profile_form.cleaned_data.get('phone'),
                                                           dob=profile_form.cleaned_data.get('dob'))
            get_guide_city_list = guide_city.objects.filter(guide_id=request.session.get('user')['user_id']). \
                values_list('city_id', flat=True)

            if is_guide:
                city_hidden = profile_form.cleaned_data.get('city_hidden')
                city_id_list = get_city_id_list(city_hidden)
                # remove the city from city_guide table if city exist in table but at the time of guide update same city
                # id gets removed
                removed_city_id_list = list_comapre(get_guide_city_list, city_id_list)
                delete_city = guide_city.objects.filter(city_id__in=removed_city_id_list,
                                                        guide_id=profile_form.cleaned_data.get('userid')).delete()
                for city_id in city_id_list:
                    city_obj = city.objects.filter(city_id=city_id).first()
                    if city_obj:
                        check_city_exist = guide_city.objects.filter(city_id=city_id,
                                                                     guide_id=request.session.get('user')['user_id'])
                        if not check_city_exist:
                            guide_city.objects.create(guide_id=request.session.get('user')['user_id'], city_id=city_id)

            message = "User details updated successfully!"
            success = 1
        request.user_form = user_form
        request.profile_form = profile_form
        context = {
            'success': success,
            'user_form': user_form,
            'message': message,
            'profile_form': profile_form,
            'JS_CSS_VERSION': settings.JS_CSS_VERSION
        }

        # template = 'user/update_user.html' if success == 0 else 'site/index.html'
        return render(request, 'user/update_user.html', context)


class ChangePassword(View):
    form_class = ChangePasswordForm()

    def get(self, request, pk):
        form = ChangePasswordForm(request.POST or None)
        context = {'form': form, 'JS_CSS_VERSION': settings.JS_CSS_VERSION}
        template = 'user/change_password.html'
        return render(request, template, context)

    def post(self, request, pk):
        error = 1
        message = ''
        form = ChangePasswordForm(request.POST or None)
        if form.is_valid():
            if form.compare_password():
                status = 403
                error = 1
                message = _("New and confirm password should be same!")
                form = ChangePasswordForm()
            elif not form.compare_password():
                status = 200
                salt = form.cleaned_data.get('salt')
                hashed_password = form.get_encrypyt_password()
                update_user_pass = user.objects.filter(user_id=pk).update(password=hashed_password, salt=salt)
                error = 0
                message = _("Password change successfully!")
        context = {
            'form': form,
            'error': error,
            'message': message,
            'JS_CSS_VERSION': settings.JS_CSS_VERSION
        }
        template = 'site/index.html' if error == 0 else 'user/change_password.html'
        return render(request, template, context)