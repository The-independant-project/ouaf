from django.contrib import admin
from .models import *

@admin.register(Person)
@admin.register(Event)
@admin.register(MemberPayment)
@admin.register(Animal)
class DefaultAdminTemplate(admin.ModelAdmin):
    pass