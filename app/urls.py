from django.urls import path, include
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(views.home), name='home'),
    path('list_content/<int:pk>', views.content_list, name='content_list'),
    path('list_content_moderate/<int:pk>', views.content_list_moderate, name='content_list_moderate'),
    path('moderation_home/', views.moderation_home, name='moderation_home'),
    path('view_content/<int:pk>', views.content_view, name='content_view'),
    path('approve_content/<int:pk>', views.approve_content, name='approve_content'),
    path('reject_content/<int:pk>', views.reject_content, name='reject_content'),
    path('json_screen/<uuid:token_screen>', views.json_screen, name='json_screen'),
    path ('add_content', views.ContentCreateImage, name="add_content"),
    path('display/<uuid:token_screen>', views.display, name='display'),
]