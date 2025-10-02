from django.contrib import admin
from chatbot.models import Document, FAQ

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('category', 'sub_category', 'solution')
    fields = ('category', 'sub_category', 'solution')
    search_fields = ('category', 'sub_category', 'solution')

admin.site.register(Document, DocumentAdmin)


class FAQAdmin(admin.ModelAdmin):
    list_display = ('category', 'question', 'answer')
    fields = ('category', 'question', 'answer')
    search_fields = ('category', 'question', 'answer')

admin.site.register(FAQ, FAQAdmin)