from django import forms
from django.contrib import admin

from raceratings.models import RatingPageContentBlock


class BlockAdminForm(forms.ModelForm):
    # content = forms.CharField(widget=CKEditorWidget()) # TODO: To markdown

    class Meta:
        model = RatingPageContentBlock
        fields = (
            'content_type',
            'content',
        )


class PageContentBlockInline(admin.StackedInline):
    model = RatingPageContentBlock
    extra = 0
    form = BlockAdminForm


class PageContentAdmin(admin.ModelAdmin):
    inlines = [
        PageContentBlockInline
    ]
    list_filter = ('content_type',)
    search_fields = ('content_label',)

    readonly_fields = (
        'content_object',
    )
    fieldsets = (
        ('Page Meta', {
            'fields': (
                'content_object',
            ),
        }),
    )
