from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import *


class UserModelAdmin(BaseUserAdmin):
    list_display=['id','email','name','is_admin']
    list_filter=['is_admin',]
    fieldsets=[
         ("User Credentials", {"fields":["email",
         "password"]}),
        ("Personal Info",{"fields":["name"]}),
        ("Permissions",{"fields":["is_admin"]}),
    ]
    search_fields=["email"],
    ordering = ["email", "id"] 
    filter_horizontal=[]

class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'receiver__username')
    ordering = ('-created_at',)
    list_editable = ('status',)
    date_hierarchy = 'created_at'

admin.site.register(FriendRequest, FriendRequestAdmin)

admin.site.register(User,UserModelAdmin)


