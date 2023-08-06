
from django.conf.urls import url

from comments import views


app_name = 'comments'


urlpatterns = [

    url(r'^create/$', views.create_comment, name='create'),

    url(r'^list/(?P<app_label>\w+)/(?P<model>\w+)/(?P<object_id>\d+)/$',
        views.get_comments, name='list'),

]
