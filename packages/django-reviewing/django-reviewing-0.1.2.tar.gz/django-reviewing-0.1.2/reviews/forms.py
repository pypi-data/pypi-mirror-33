from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Review


class ReviewAdminForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = (
            'active',
            'highlight',
            'score',
            'title',
            'comment',
            'display_date',
            'user',
            'user_name',
            'user_email',
            'source',
            'object_id',
            'content_type',
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        highlight = cleaned_data.get('highlight', False)

        if highlight:
            queryset = Review.objects.filter(active=True, highlight=True, content_type=self.instance.content_type, object_id=self.instance.object_id)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                self.add_error('highlight', _('There already is a highlighted review for this object'))

        return cleaned_data
