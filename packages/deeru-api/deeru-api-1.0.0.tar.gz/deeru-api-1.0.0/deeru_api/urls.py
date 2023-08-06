from django.urls import path


from deeru_api import views

app_name = 'api'

urlpatterns = [
    path('app_config', views.app_config_view, name='app_config'),
    path('article/<int:article_id>', views.detail_article_view, name='detail_article'),
    path('article_list', views.article_list_view, name='article_list'),

    path('category/<int:category_id>', views.detail_category_view, name='detail_category'),
    path('category_list', views.category_list_view, name='category_list'),
    path('category_tree', views.category_tree_view, name='category_tree'),

    path('tag/<int:tag_id>', views.detail_tag_view, name='detail_tag'),
    path('tag_list', views.tag_list_view, name='tag_list'),

    path('comment/create', views.create_comment, name='create_comment'),
    path('comment_list', views.comment_list_view, name='comment_list'),

]
