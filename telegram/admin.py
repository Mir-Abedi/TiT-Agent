from django.contrib import admin
from telegram.models import UserMessage, BotMessage

class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'chat_id', 'text', 'timestamp')
    fields = ('user_id', 'chat_id', 'text', 'timestamp', 'bot_message')
    search_fields = ('user_id', 'chat_id', 'text')

admin.site.register(UserMessage, UserMessageAdmin)

class BotMessageAdmin(admin.ModelAdmin):
    list_display = ('user_message', 'text', 'timestamp')
    fields = ('user_message', 'text', 'timestamp')
    search_fields = ('user_message', 'text')

admin.site.register(BotMessage, BotMessageAdmin)