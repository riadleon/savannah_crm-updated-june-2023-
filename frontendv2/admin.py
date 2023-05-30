from django.contrib import admin
from django.utils.safestring import mark_safe

from frontendv2.models import EmailRecord, ManagerInvite, PasswordResetRequest, PublicDashboard
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

class SessionAdmin(admin.ModelAdmin):
    def user(self, obj):
        session_user = obj.get_decoded().get('_auth_user_id')
        user = User.objects.get(pk=session_user)
        return user.username
    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', 'user', '_session_data', 'expire_date']
    readonly_fields = ['user', '_session_data']
    exclude = ['session_data']
    date_hierarchy='expire_date'
admin.site.register(Session, SessionAdmin)

# Register your models here.
class EmailAdmin(admin.ModelAdmin):
    list_display = ["when", "recipient_display", "category", "subject", "sender", "ok"]
    list_filter = ["ok", "when", "category", ("sender", admin.RelatedOnlyFieldListFilter)]
    readonly_fields = ["when", "sender", "member", "email", "subject", "body", "category", "ok"]
    search_fields = ["subject", "body", "to"]

    def recipient_display(self, record):
        if record.member is not None:
            return "%s <%s>" % (record.member.name, record.email)
        else:
            return record.email

    recipient_display.short_description = "To"

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False


admin.site.register(EmailRecord, EmailAdmin)

class ManagerInviteAdmin(admin.ModelAdmin):
    list_display = ("community", "email", "invited_by", "timestamp", "expires")
    list_filter = ("community", "invited_by", "timestamp", "expires")
admin.site.register(ManagerInvite, ManagerInviteAdmin)

class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ("user", "email",  "timestamp", "expires")
    list_filter = ("timestamp", "expires")
admin.site.register(PasswordResetRequest, PasswordResetAdmin)

class PublicDashboardAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'link', 'community', 'page', 'created_by', 'created_at', 'view_count')
    list_filter = ('page', 'community', 'created_at')
    def link(self, dashboard):
        return mark_safe("<a href=\"%s\" target=\"_blank\">Open</a>" % dashboard.get_absolute_url())
    link.short_description = "URL"
admin.site.register(PublicDashboard, PublicDashboardAdmin)