from django import forms
from .models_user import user,user_profile,user_password_tokens
from  phonenumber_field.formfields import PhoneNumberField
import secrets
from .services import encrypt_val,decrypt_val,expire_user_password_tokens,get_salt,hashed_password
from django.http import QueryDict
from parsley.decorators import parsleyfy


from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate


class UserRegistrationForm(forms.ModelForm):

    first_name = forms.CharField(
        label='First Name',
        required=True,
        widget=forms.TextInput(attrs={"placeholder": ""})
    )

    last_name = forms.CharField(
        label='Last Name',
        required=True,
        widget=forms.TextInput(attrs={"placeholder": ""})
    )

    email = forms.EmailField(
        label='Email',
        required=True,
    )

    password = forms.CharField(
        label='Password',
        required=True,
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput()
    )
    SEX_CHOICES = (
        (1, 'Female',),
        (2, 'Male',),
    )
    sex = forms.ChoiceField(
        label="Sex",
        choices=SEX_CHOICES,
    )
    # profile_picture = forms.ImageField(required=False)

    salt = forms.CharField(
        widget=forms.HiddenInput(),
        required = False
    )

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['salt'].initial = get_salt()

    class Meta:
        model = user
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
            'profile_picture',
            'sex',
            'salt'
        ]

    def clean(self):
        if self.data.get('user_id'):
            self.fields['password'].required = False
            return self.cleaned_data.get('password')

    # Duplicate in ResetPasswordForm
    def clean_password(self):
        password = self.cleaned_data.get('password')
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if user.objects.filter(email=email).count() > 0:
            raise forms.ValidationError('Account already exists with entered email')
        return email

    def get_encrypyt_password(self):
        return hashed_password(self.cleaned_data.get('password'), self.cleaned_data.get('salt'))


class DateInput(forms.DateInput):
    input_type = 'date'


class UserProfileForm(forms.ModelForm):

    phone = PhoneNumberField(
        widget=forms.TextInput(
            attrs={'placeholder': "Phone number"}),
            label="Phone number",
            required=True,
            help_text="Phone Number Format: +12032391234"
    )

    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    guide_choice = [(1, 'Yes',), (0, 'No',)]
    is_guide = forms.IntegerField(widget=forms.RadioSelect(choices=guide_choice), required=False)
    city_hidden = forms.CharField(widget=forms.HiddenInput(), required=False)
    city = forms.CharField(widget=forms.TextInput(attrs={'class': "typeahead tm-input form-control tm-input-info"}),  required=False)


    class Meta:
        model = user_profile
        fields = [
            'dob',
            'phone',
            'user_id',
            'is_guide',
            'city_hidden',
            'city'
        ]
        widgets = {
            'dob': DateInput(),
        }

    def clean_city(self):
        if self.cleaned_data.get('is_guide') == 1:
            if self.cleaned_data.get('city_hidden') == '':
                raise forms.ValidationError('City is required field!')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if user_profile.objects.filter(phone=phone).count() > 0:
            raise forms.ValidationError('Account already exists with entered phone')
        return phone


class ForgotPasswordForm(forms.ModelForm):

    email = forms.EmailField(
        label='Email',
        required=True,
    )

    user_id = ""

    def __init__(self, *args, **kwargs):
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)
        self.user_id = ''
        self.secret_key = 'tr1p1an1@2019'

    class Meta:
        model = user
        fields = [
            'email',
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email

    def email_exists(self):
        status=False
        email = self.cleaned_data.get('email')
        user_obj = user.objects.filter(email=email,active=1)
        if user_obj.count() > 0:
            self.user_id = str(user_obj[0].user_id)
            status=True
        return status

    def get_reset_token_params(self):
        query_string = ''
        if(self.user_id != ''):
            token=secrets.token_urlsafe(15)
            token_obj = user_password_tokens(user_id=self.user_id, token=token)
            token_obj.save()

            if token_obj.pk is not None:
                expire_user_password_tokens(self.user_id, token_obj.pk)
                id = encrypt_val(self.user_id)
                token = encrypt_val(token)
                q = QueryDict(mutable=True)
                q['id'] = id
                q['token'] = token
                query_string = q.urlencode()

        return query_string

    def get_decrypted_user_id(self, token):
        id = decrypt_val(token)
        return id

    # def generate_reset_token(self, user_id, token):
    #     return jwt.encode({'user_id': user_id, 'token':token}, self.secret_key, algorithm='HS256')

class ResetPasswordForm(forms.ModelForm):

    password = forms.CharField(
        label='Password',
        min_length=8,
        max_length=20,
        required=True,
        widget=forms.PasswordInput()
    )

    reset_password = forms.CharField(
        label='Reset Password',
        required=True,
        widget=forms.PasswordInput()
    )

    class Meta:
        model = user
        fields = [
            'password',
            'reset_password'
        ]

    # Duplicate in UserRegistrationForm
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Password too short')
        return password

    def clean_reset_password(self):
        reset_password = self.cleaned_data.get('reset_password')
        password = self.cleaned_data.get('password')
        if password != reset_password:
            raise forms.ValidationError('Passwords are not identical')
        return reset_password

    def update_password(self, user_id, token_id):
        status=False
        password = self.cleaned_data.get('password')
        try:
            salt=get_salt()
            h_password=hashed_password(password,salt)
            num = user.objects.filter(user_id=user_id).update(password=h_password,salt=salt);
            if num>0:
                user_password_tokens.objects.filter(token_id=token_id).update(used=1);
                user_password_tokens.objects.filter(user_id=user_id).update(expired=1);
                status=True
        except Exception as e:
            pass

        return status

@parsleyfy
class LoginForm(forms.ModelForm):

    email = forms.EmailField(
        label='Email',
        required=True,
    )

    password = forms.CharField(
        label='Password',
        required=True,
        widget=forms.PasswordInput()
    )

    class Meta:
        model = user
        fields = [
            'email',
            'password'
        ]

    def get_user(self):
        try:
            user_obj = user.objects.filter(email=self.cleaned_data.get('email'), active=1)
            if (user_obj.count()>0):
                h_password = hashed_password(self.cleaned_data.get('password'), user_obj[0].salt)
                user_obj = user.objects.filter(email=self.cleaned_data.get('email'),password=h_password, active=1)
                return user_obj
        except Exception as e:
            pass
        return None


@parsleyfy
class UpdateUserRegistrationForm(forms.ModelForm):

    first_name = forms.CharField(
        label='First Name',
        required=True,
        widget=forms.TextInput(attrs={"placeholder": ""})
    )

    last_name = forms.CharField(
        label='Last Name',
        required=True,
        widget=forms.TextInput(attrs={"placeholder": ""})
    )

    email = forms.EmailField(
        label='Email',
        required=True,
    )

    SEX_CHOICES = (
        (1, 'Female',),
        (2, 'Male',),
    )
    sex = forms.ChoiceField(
        label="Sex",
        choices=SEX_CHOICES,
    )
    profile_picture = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super(UpdateUserRegistrationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = user
        fields = [
            'first_name',
            'last_name',
            'email',
            'profile_picture',
            'sex',
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if user.objects.filter(email=email, active=1).exclude(user_id__in=[self.data.get('userid')]).count() > 0:
            raise forms.ValidationError('Account already exists with entered email')
        return email

@parsleyfy
class UpdateUserProfileForm(forms.ModelForm):

    phone = PhoneNumberField(
        widget=forms.TextInput(
            attrs={'placeholder': "Phone number"}),
            label="Phone number",
            required=True,
            help_text="Phone Number Format: +12032391234"
    )

    userid = forms.CharField(widget=forms.HiddenInput(), required=False)
    guide_choice = [(1, 'Yes',), (0, 'No',)]
    is_guide = forms.IntegerField(widget=forms.RadioSelect(choices=guide_choice, attrs={'disabled': 'True'}), required=False)
    city_hidden = forms.CharField(widget=forms.HiddenInput(), required=False)
    city = forms.CharField(widget=forms.TextInput(attrs={'class': "typeahead tm-input form-control tm-input-info"}),  required=False)


    class Meta:
        model = user_profile
        fields = [
            'dob',
            'phone',
            'userid',
            'is_guide',
            'city_hidden',
            'city'
        ]
        widgets = {
            'dob': DateInput(),

        }

    def clean_is_guide(self):
        return self.cleaned_data.get('is_guide')

    def clean_city(self):
        if self.cleaned_data.get('city_hidden') == '':
            raise forms.ValidationError('City is required field!')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if user_profile.objects.filter(phone=phone).exclude(user_id__in=[self.data.get('userid')]).count() > 0:
            raise forms.ValidationError('Account already exists with entered phone')
        return phone


@parsleyfy
class ChangePasswordForm(forms.Form):

    new_password = forms.CharField(
        label='New Password',
        required=True,
        widget=forms.PasswordInput()
    )

    confirm_password = forms.CharField(
        label='Confirm Password',
        required=True,
        widget=forms.PasswordInput()
    )

    salt = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = user
        fields = ['new_password', 'confirm_password']

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['salt'].initial = get_salt()

    def compare_password(self):
        status = False
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if new_password != confirm_password:
            status = True
        return status

    def get_encrypyt_password(self):
        return hashed_password(self.cleaned_data.get('new_password'), self.cleaned_data.get('salt'))