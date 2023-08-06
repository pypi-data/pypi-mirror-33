
from django import template
from django.contrib.contenttypes.models import ContentType

from ..forms import CommentForm


register = template.Library()


@register.inclusion_tag('comments/index.html', takes_context=True)
def render_comments(context, app_label, model, object_id):

    content_type = ContentType.objects.get_by_natural_key(app_label, model)

    initial = {'content_type': content_type, 'object_id': object_id}

    form = CommentForm(context.request, initial=initial)

    return {
        'app_label': app_label,
        'model': model,
        'object_id': object_id,
        'form': form
    }
