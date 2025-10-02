from django.contrib import admin
from telegram.models import UserMessage, BotMessage

class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'chat_id', 'text', 'timestamp')
    fields = ('user_id', 'chat_id', 'text', 'timestamp', 'bot_message')
    readonly_fields = fields
    search_fields = ('user_id', 'chat_id', 'text')

admin.site.register(UserMessage, UserMessageAdmin)

class BotMessageAdmin(admin.ModelAdmin):
    list_display = ('user_message', 'text', 'timestamp')
    fields = ('user_message', 'text', 'timestamp')
    readonly_fields = fields
    search_fields = ('user_message', 'text')

admin.site.register(BotMessage, BotMessageAdmin)