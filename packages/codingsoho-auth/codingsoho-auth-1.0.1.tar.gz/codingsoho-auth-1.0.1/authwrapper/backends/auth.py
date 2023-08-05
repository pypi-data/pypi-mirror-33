from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib import auth

#from django.core.exceptions import ObjectDoesNotExist

from authwrapper.models import MyUser, WechatUserProfile

from weixin.client import WeixinMpAPI
#from weixin.oauth2 import OAuth2AuthExchangeError

#UserModel = 'authwrapper.User' #
#UserModel = settings.AUTH_USER_MODEL
UserModel = get_user_model()

class MyBackend(object):
    """Allows user to sign-in using email, username or phone_number."""
    def authenticate(self, username=None, password=None, **kwargs):  
    #def authenticate(self, account_type = None, username=None, password=None, **kwargs):      

        '''
        try:
            """login with user info directly"""
            if kwargs['kwargs']['user'] :
                return kwargs['kwargs'].get('user',None)
        except:
            pass
       '''

        try:
            """login with user info directly"""
            if kwargs['user'] :
                if isinstance(kwargs['user'], UserModel):
                    return kwargs.get('user',None)
                else: #wechat user
                    return None
        except:
            pass

        user = None
        if username is None and kwargs.get(UserModel.USERNAME_FIELD,None) is None:
            return None

        try:
            """ fail? why 
            user = UserModel.objects.filter(username=username).first()  
            user = UserModel.objects.get(username=username) 
            """

            """ 'username' for mail registion, 'phone' for phone registion 
            here let's take username as the input in login textbox """
            '''
            user = UserModel._default_manager.using(self._db).get(**{
                UserModel.USERNAME_FIELD: username
            })
            '''

            """if allow mix login options
            username/phone/mail """
            if True == settings.ACCOUNT_ALLOW_MIX_TYPE_LOGIN:
                if '@' in username:
                    user = UserModel._default_manager.get(email=username)
                elif '+' in username[0]: # to be precise
                    user = UserModel._default_manager.get(phone=username)
                else:
                    user = UserModel._default_manager.get(username=username)
            else:    
                user = UserModel._default_manager.get_by_natural_key(username)
            
            if user.check_password(password):
                return user

            # OR-OK check_password(user.password, password)
                
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            else:
                return None

    def user_can_authenticate(self, user):
        """Reject users with is_active=False. Custom user models that don't have that attribute are allowed."""
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def get_user(self, user_id):
        
        try:
            user = UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None


class WechatBackend(object):

    def authenticate(self, request, user):
        obj = None
        cur_user = auth.get_user(request)
        profile, created = WechatUserProfile.objects.get_or_create(openid = user['openid'])

        if created is False:
            obj = profile.user            
            if profile.user is None:
                if cur_user.is_active and not cur_user.is_anonymous() and cur_user is not None:
                    profile.user =  cur_user
                    profile.save()
        else:
            profile.unionid = user['unionid']
            #profile.privilege = user['privilege'] #privilege is list
            profile.city = user['city']
            profile.country = user['country']
            profile.language = user['language']
            if 1 == user['sex']:
                profile.sex = 'male'
            else:
                profile.sex = 'female'
            profile.nickname = user['nickname']
            profile.headimgurl = user['headimgurl']
            if cur_user.is_active and not cur_user.is_anonymous() and cur_user is not None:
                profile.user = cur_user
            profile.save()
            obj = request.user

        request.session['wechat_id'] = profile.id
        # request._cached_user = obj

        return obj

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

        # if not hasattr(request, '_cached_user'):
        #     request._cached_user = auth.get_user(request)
        # return request._cached_user

    def get_wechat_user(self, request):
        wechat_id = request.session.get("wechat_id", None)
        if wechat_id:
            try:
                wechat = WechatUserProfile.objects.get(pk=wechat_id)
                return wechat
            except:
                pass
        return None
            
class SettingsBackend(object):
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'pbkdf2_sha256$30000$Vo0VlMnkR4Bk$qEvtdyZRWTcOsCnI/oQ7fVOu1XAURIZYoOZ3iq8Dr4M='
    """

    def authenticate(self, request, username=None, password=None):
        login_valid = (settings.ADMIN_LOGIN == username)
        pwd_valid = check_password(password, settings.ADMIN_PASSWORD)
        if login_valid and pwd_valid:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. There's no need to set a password
                # because only the password from settings.py is checked.
                user = User(username=username)
                user.is_staff = True
                user.is_superuser = True
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None            