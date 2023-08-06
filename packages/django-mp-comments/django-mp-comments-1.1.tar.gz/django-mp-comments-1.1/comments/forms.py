
from django import forms

from captcha.fields import ReCaptchaField

from comments.models import Comment


class CommentForm(forms.ModelForm):

    captcha = ReCaptchaField()

    def __init__(self, request, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.request = request

        if self._is_user_authenticated():
            self.initial.update({
                'name': request.user.get_full_name(),
                'email': request.user.email
            })

    def save(self, commit=True):

        comment = super(CommentForm, self).save(commit=False)
        comment.is_active = True  # TODO: move this option to settings
        comment.ip_address = self._get_ip()

        if self._is_user_authenticated():
            comment.user = self.request.user

        if commit:
            comment.save()

        return comment

    def _is_user_authenticated(self):
        try:
            return self.request.user.is_authenticated()
        except TypeError:  # Django >= 1.11
            return self.request.user.is_authenticated

    def _get_ip(self):
        request = self.request
        ip = request.META.get('REMOTE_ADDR', None)
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        return ip.replace(',', '').split()[0]

    class Meta:
        model = Comment
        fields = ['content_type', 'object_id', 'name', 'email', 'text']
        widgets = {
            'content_type': forms.HiddenInput,
            'object_id': forms.HiddenInput
        }
