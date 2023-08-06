
from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from comments.models import Comment, CommentAnswer


class CommentForm(forms.ModelForm):

    text = forms.CharField(
        label=_('Comment'), widget=forms.Textarea(attrs={'readonly': True}))

    answer_text = forms.CharField(label=_('Answer'), widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        answer = kwargs['instance'].answer
        if answer:
            kwargs['initial'] = {'answer_text': answer.text}
        super(CommentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Comment
        fields = ['text']


class CommentsAdmin(admin.ModelAdmin):

    form = CommentForm

    list_display = ['id', 'name', 'email', 'created', 'is_active', 'has_answer']
    list_editable = ['is_active']
    list_filter = ['is_active']
    list_display_links = ['id', 'name']

    def has_answer(self, obj):
        return bool(obj.answer)

    has_answer.boolean = True
    has_answer.short_description = _('Has answer')

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        answer = obj.answer if obj.answer else CommentAnswer()
        answer.user = request.user
        answer.text = form.cleaned_data['answer_text']
        answer.save()

        obj.answer = answer
        obj.save()


admin.site.register(Comment, CommentsAdmin)
