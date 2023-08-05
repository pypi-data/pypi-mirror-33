from django import forms

from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.admin import widgets
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import datetime

from phonenumber_field.formfields import PhoneNumberField as FormPhoneNumberField
from phone_login.models import PhoneToken

#from .models import MyUser
from .users import UserModel, UsernameField
User = UserModel()


class RegistrationForm(forms.Form):
    """Register form with phone verification code
    """
    #phone = forms.CharField(label='Phone', max_length=18)
    phone = FormPhoneNumberField(label='Phone')
    password = forms.CharField(label='Set Password', widget=forms.PasswordInput)
    otp = forms.CharField(label='One-Time Password',  max_length=10) 

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        users = UserModel().objects.filter(phone=phone).first()
        if users and users.is_active:
            raise forms.ValidationError('User Exist!')
            return phone

        '''
        #used if phone is CharField

        import re 
        pattern = re.compile(r'^\+86(130|131|132|133|134|135|136|137|138|139)\d{8}$') 
        match = pattern.search(phone) 
        if not match:
            raise forms.ValidationError('Please input valid phone number !')
        '''   
        return phone

    def clean_otp(self):
        phone_number = self.cleaned_data.get('phone',None)
        if phone_number is None:
            return

        otp = self.cleaned_data.pop('otp')
        phone_token = None

        timestamp_difference = datetime.datetime.now() - datetime.timedelta(
            minutes=getattr(settings, 'PHONE_LOGIN_MINUTES', 10)
        )

        try:
            phone_token = PhoneToken.objects.get(
                phone_number=phone_number,
                otp=otp,
                used=False,
                timestamp__gte=timestamp_difference
            )

        except PhoneToken.DoesNotExist:
            raise forms.ValidationError('invalid otp!')

        phone_token.used = True
        phone_token.attempts = phone_token.attempts + 1
        phone_token.save()                    


class UserUpdateForm(forms.ModelForm):
    """ actual step to update user information after verification pass"""
    required_css_class = 'required'
    phone = forms.CharField(label='phone')
    birthday = forms.DateField(label='birthday', 
        #widget=forms.DateInput(attrs={'cols': 10, 'rows': 50, 'readonly':'readonly','disable':True}),  #WORK
        #widget=SelectDateWidget(),
        widget=widgets.AdminDateWidget(),
        error_messages={'required':'birthday required'})
    #sex = forms.ChoiceField(label='sex', empty_label=None)


    #can specify widget or widget attribute in init function
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['birthday'].widget = widgets.AdminDateWidget()
        self.fields['sex'].empty_label = None
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['phone'].widget.attrs['readonly'] = True


    ''' NOT WORK
    widgets = {
        'phone': forms.CharField(attrs={'cols': 10, 'rows': 50, 'readonly':'readonly','disable':True}),
    }
    '''

    def clean_phone(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            return instance.phone
        else:
            return self.cleaned_data['phone']

    class Meta:
        model = User
        fields = (UsernameField(),'first_name','last_name','sex','birthday','nickname','image') 
        #exclude = ('password',)

class RegistrationForgetForm(RegistrationForm):
    #password = forms.CharField(label='New Password', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(RegistrationForgetForm, self).__init__(*args, **kwargs)
        self.fields['password'].label = 'New Password'

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        users = UserModel().objects.filter(phone=phone).first()
        if not users or not users.is_active:
            raise forms.ValidationError('User is not Exist!')
            return phone

        return phone


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password.
    used in admin """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'phone')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

#refer to django/contrib/auth/forms.py
class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    used in admin
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = '__all__' 
        # fields = ('email', 'password', 'first_name', 'last_name', 'is_active', 'is_staff', 'image')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]