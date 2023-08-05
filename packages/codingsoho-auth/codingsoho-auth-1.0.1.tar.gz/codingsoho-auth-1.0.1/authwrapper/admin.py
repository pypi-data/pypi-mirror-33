from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session

from .models import MyUser, WechatUserProfile
from .forms import UserCreationForm, UserChangeForm

#refer to django/contrib/auth/admin.py
class UserAdmin(BaseUserAdmin):
    ''' 
    The forms to add and change user instances
    '''
    form = UserChangeForm
    add_form = UserCreationForm

    '''
    The fields to be used in displaying the User model.
    These override the definitions on the base UserAdmin
    that reference specific fields on auth.User.
    '''

    list_display = ('username', 'phone','email', 'sex','birthday','nickname','is_staff')
    list_filter = ('account_type','is_staff',)
    fieldsets = (
        (None, 
        	{'fields': 
        	('username','phone','email', 'password')}),
        ('Personal info', 
        	# {'fields': ('first_name','last_name', 'sex','birthday','nickname','account_type','image')}),
            {'fields': ('first_name','last_name', 'sex','birthday','nickname','user_role','image')}),
        ('Permissions', 
        	{'fields': ('is_staff','is_active', 'is_superuser','groups', 'user_permissions')}),
        ('Important dates', 
            {'fields': ('last_login', 'date_joined')}),
    )
    
    '''
    add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    overrides get_fieldsets to use this attribute when creating a user.
    '''
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','phone', 'email', 'password1', 'password2')}
        ),
    )
    search_fields = ('phone','email',)
    ordering = ('username',)
    # filter_horizontal = ('groups', 'user_permissions',) #inherit from base

    view_on_site = False

class WechatUserProfileAdmin(admin.ModelAdmin):
    list_display = ["openid", "unionid", "nickname"]
    class Meta:
        model = WechatUserProfile

class PermissionAdmin(admin.ModelAdmin):
    list_display = ["content_type", "name", "codename"]
    list_filter = ["content_type"]
    class Meta:
        model = Permission

class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ["app_label", "model"]
    class Meta:
        model = ContentType

class SessionAdmin(admin.ModelAdmin):
    list_display = ["session_key","expire_date" ,"session_data", ]
    class Meta:
        model = Session

    list_per_page = 10
    list_max_show_all = 20

# Now register the new UserAdmin...
admin.site.register(MyUser, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
#admin.site.unregister(Group)
admin.site.register(WechatUserProfile, WechatUserProfileAdmin)

# admin.site.register(Group, GroupAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(ContentType, ContentTypeAdmin)

admin.site.register(Session, SessionAdmin)
