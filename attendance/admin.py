from django.contrib import admin
from .models import Attendance, AuthorizedDevice

admin.site.register(Attendance)
admin.site.register(AuthorizedDevice)
