from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'age', 'is_above_18', 'agreed_to_terms', 'created_at')
    search_fields = ('user__username', 'phone_number')
    list_filter = ('is_above_18', 'agreed_to_terms')
