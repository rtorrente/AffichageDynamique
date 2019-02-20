from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('', login_required(views.home), name='home'),
    path('list_content/<int:pk>', login_required(views.content_list), name='content_list'),
    path('list_content_moderate/<int:pk>', login_required(views.content_list_moderate), name='content_list_moderate'),
    path('moderation_home/', login_required(views.moderation_home), name='moderation_home'),
    path('view_content/<int:pk>', login_required(views.content_view), name='content_view'),
    path('approve_content/<int:pk>', login_required(views.approve_content), name='approve_content'),
    path('reject_content/<int:pk>', login_required(views.reject_content), name='reject_content'),
    path('add_content', login_required(views.ContentCreateImage), name="add_content"),

    path('json_screen/<uuid:token_screen>', views.json_screen, name='json_screen'),  # NoLoginRequired
    path('display/<uuid:token_screen>', views.display, name='display'),  # NoLoginRequired
]