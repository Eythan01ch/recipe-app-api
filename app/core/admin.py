"""
Django admin customisation
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


class UserAdmin(BaseUserAdmin):
	"""Define the admin pages for users"""
	ordering = ['id']
	list_display = ['email', 'name', ]
	readonly_fields = ['last_login', ]

	fieldsets = (
		# Email, Password
		(None, {'fields': ('email', 'password')}),
		# Permissions
		(
			_('Permissions'),
			{
				'fields':
					('is_staff',
					 'is_active',
					 'is_superuser',
					 )
			}
		),
		# Dates
		(_('Important Dates'), {'fields': ('last_login',)}),

	)

	add_fieldsets = (
		(
			None,
			{
				'classes': ('wide',),
				'fields':  (
					'email',
					'password1',
					'password2',
					'name',
					'is_active',
					'is_staff',
					'is_superuser',
				)
			}
		),
	)


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)

