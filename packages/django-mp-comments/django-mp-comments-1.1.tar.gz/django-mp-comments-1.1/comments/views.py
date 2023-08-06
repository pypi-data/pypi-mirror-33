
from django.shortcuts import render
from django.http.response import JsonResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType

from comments.models import Comment
from comments.forms import CommentForm


LIST_ITEM_TEMPLATE = 'comments/list_item.html'


@require_POST
def create_comment(request):

    form = CommentForm(request, data=request.POST)

    if form.is_valid():
        comment = form.save()
        return render(request, LIST_ITEM_TEMPLATE, {'comment': comment})

    return render(request, 'comments/form.html', {'form': form}, status=400)


def get_comments(request, app_label, model, object_id):

    content_type = ContentType.objects.get_by_natural_key(app_label, model)

    comments = Comment.objects.filter(
        is_active=True, content_type=content_type, object_id=object_id
    ).select_related('answer').order_by('-created')

    paginator = Paginator(comments, 10)

    page_number = request.GET.get('page', 1)

    page = paginator.page(page_number)

    html = ''

    for comment in page.object_list:
        html += render_to_string(LIST_ITEM_TEMPLATE, {'comment': comment})

    return JsonResponse({
        'is_next_page_available': page.has_next(),
        'html': html
    })
