from django.conf.urls import patterns, include, url

from component.views import *

urlpatterns = patterns('',
    url(r'^$',component_list,name="component_list"),
    url(r'^new/$',component_add),
    url(r'^new/category/new/$',CategoryAddView.as_view(),name="category_add_in_component"),
    #url(r'^new/category/new$',category_add,name="category_add_in_component"),
    #url(r'^new/post/new$',post_add,name="post_add_in_component"),
    url(r'^new/post/new/$',PostAddView.as_view(),name="post_add_in_component"),
    url(r'^(?P<category_name>.*)/(?P<component_name>.*)/edit/$',component_edit),
    url(r'^(?P<category_name>.*)/(?P<component_name>.*)/delete/$',component_delete),
    url(r'^(?P<category_name>.*)/edit/$',category_edit),
    url(r'^(?P<category_name>.*)/delete/$',category_delete),
    url(r'^(?P<category_name>.*)/(?P<component_name>.*)/$',component_detail,name="component_detail"),
    url(r'^(?P<category_name>.*)/$',category_edit),
)
