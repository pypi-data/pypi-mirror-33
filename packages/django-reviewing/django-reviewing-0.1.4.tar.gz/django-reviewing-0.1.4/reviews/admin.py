from django.contrib import admin
from django.contrib.contenttypes.admin import (
    GenericStackedInline, GenericTabularInline
)
from django.utils.translation import gettext_lazy as _

from .admin_filter import get_generic_foreign_key_filter
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('score', 'name', 'email', 'title', 'content', 'display_date')
    list_filter = ('score', get_generic_foreign_key_filter('Content', 'content'))

    fieldsets = (
        (None, {
            'fields': ('active', 'user', 'user_name', 'user_email', 'score', 'title', 'comment', 'display_date', 'source')
        }),
        ('Generic foreign key', {
            'description': _('The object connected to the review. This can be empty for a global review.'),
            'fields': ('content_type', 'object_id', )
        }),
    )


class ReviewTabularInlineAdmin(GenericTabularInline):
    model = Review
    extra = 1


class ReviewStackedInlineAdmin(GenericStackedInline):
    model = Review
    extra = 1
