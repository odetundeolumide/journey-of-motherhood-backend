from django.contrib import admin

from UserProfile.models import CustomUser

# Register your models here.

admin.site.register((CustomUser, ))