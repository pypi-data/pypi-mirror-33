=====
codingsoho-auth
=====

codingsoho-authwrapper project is auth wrapper for authentication

Detailed documentation is in the "docs" directory.

Quick start
-----------
1. Install 'authwrapper' and 'django-phone-login', checking django-phone-login readme for configuration

2. Add "authwrapper" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'authwrapper',
		'phone_login',
    ]

3  Add configurations
	AUTH_USER_MODEL = 'authwrapper.MyUser'
	ACCOUNT_ALLOW_MIX_TYPE_LOGIN = True
	UUSLUGIFY = True
	
	AUTHENTICATION_BACKENDS = (        
    'authwrapper.backends.auth.MyBackend', 
    'authwrapper.backends.auth.WechatBackend', # if support wechat
    'django.contrib.auth.backends.ModelBackend',     
    )
	
	# if support wechat
	APP_SECRET = 
	APP_ID = 
	
	ACCOUNT_REGISTER_TYPE =  'phone' # or 'email'


2. Include the polls URLconf in your project urls.py like this::

    url(r'^authwrapper/', include('authwrapper.urls')),

3. Run `python manage.py migrate` to create the authwrapper models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a models if needed (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/authwrapper/ to participate in the auth.