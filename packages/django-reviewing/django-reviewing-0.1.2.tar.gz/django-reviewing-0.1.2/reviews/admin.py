from django.contrib import admin
from django.contrib.contenttypes.admin import (
    GenericStackedInline, GenericTabularInline
)
from django.utils.translation import gettext_lazy as _

from .forms import ReviewAdminForm
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'score', 'title', 'content', 'display_date', 'highlight')
    list_filter = ('score', 'highlight')
    form = ReviewAdminForm

    fieldsets = (
        (None, {
            'fields': ('active', 'user', 'user_name', 'user_email', 'score', 'title', 'comment', 'display_date', 'highlight')
        }),
        ('Generic foreign key', {
            'description': _('The object connected to the review. This can be empty for a global review.'),
            'fields': ('content_type', 'object_id', )
        }),
    )


class ReviewTabularInlineAdmin(GenericTabularInline):
    model = Review
    form = ReviewAdminForm
    extra = 1


class ReviewStackedInlineAdmin(GenericStackedInline):
    model = Review
    form = ReviewAdminForm
    extra = 1
