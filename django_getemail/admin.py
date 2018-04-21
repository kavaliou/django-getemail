from django.contrib import admin

from django_getemail.models import Email, EmailAttachment


@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    search_fields = ('email__uid', )
    readonly_fields = ('file', 'email')


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('uid', 'created_at', 'status')
    list_filter = ('status', )
    ordering = ('-uid', )
