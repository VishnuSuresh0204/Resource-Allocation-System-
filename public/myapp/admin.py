from django.contrib import admin
from .models import *

admin.site.register(Login)
admin.site.register(District)
admin.site.register(Citizen)
admin.site.register(Staff)
admin.site.register(Volunteer)
admin.site.register(ResourceCategory)
admin.site.register(ResourceStock)
admin.site.register(UserResourceRequest)
admin.site.register(ResourceDistribution)
admin.site.register(Notification)