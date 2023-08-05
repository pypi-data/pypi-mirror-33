from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from sitetree.admin import TreeItemAdmin, TreeAdmin, override_tree_admin, override_item_admin

from cosmicdb.models import UserSystemNotification


class UserSystemNotificationInlineAdmin(admin.TabularInline):
    model = UserSystemNotification


class UserProfileAdmin(UserAdmin):
    inlines = [
        UserSystemNotificationInlineAdmin,
    ]


user_model = get_user_model()
admin.site.register(user_model, UserProfileAdmin)


class CosmicDBTreeAdmin(TreeAdmin):
    pass


class CosmicDBTreeItemAdmin(TreeItemAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fieldsets = (
            (_('Basic settings'), {
                'fields': ('parent', 'title', 'url', 'is_right', 'is_button')
            }),
            (_('Access settings'), {
                'classes': ('collapse',),
                'fields': ('access_loggedin', 'access_guest', 'access_restricted', 'access_permissions', 'access_perm_type')
            }),
            (_('Display settings'), {
                'classes': ('collapse',),
                'fields': ('hidden', 'inmenu', 'inbreadcrumbs', 'insitetree')
            }),
            (_('Additional settings'), {
                'classes': ('collapse',),
                'fields': ('hint', 'description', 'alias', 'urlaspattern')
            }),
        )

override_tree_admin(CosmicDBTreeAdmin)
override_item_admin(CosmicDBTreeItemAdmin)
