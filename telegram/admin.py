from django.contrib import admin
from telegram.models import UserMessage, BotMessage

class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'chat_id', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user_id', 'chat_id', 'text')

admin.site.register(UserMessage, UserMessageAdmin)

class BotMessageAdmin(admin.ModelAdmin):
    list_display = ('user_message_id', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user_message_id', 'text')

admin.site.register(BotMessage, BotMessageAdmin)