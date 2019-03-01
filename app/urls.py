from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('', login_required(views.home), name='home'),
    path('list_content/<int:pk>', login_required(views.content_list), name='content_list'),
    path('list_screen/', login_required(views.list_screen), name='list_screen'),
    path('view_screen/<int:pk_screen>', login_required(views.view_screen), name='view_screen'),
    path('delete_subscription/<int:pk_sub>', login_required(views.delete_subscription), name='delete_subscription'),
    path('add_subscription/<int:pk_screen>/<str:type_sub>', login_required(views.add_subscription),
         name='add_subscription'),
    path('list_content_moderate/<int:pk>', login_required(views.content_list_moderate), name='content_list_moderate'),
    path('moderation_home/', login_required(views.moderation_home), name='moderation_home'),
    path('view_content/<int:pk>', login_required(views.content_view), name='content_view'),
    path('approve_content/<int:pk>', login_required(views.approve_content), name='approve_content'),
    path('reject_content/<int:pk>', login_required(views.reject_content), name='reject_content'),
    path('add_content_image/', login_required(views.ContentCreateImage), name="add_content_image"),
    path('add_content_youtube/', login_required(views.ContentCreateYoutube), name="add_content_youtube"),
    path('add_content_url/', login_required(views.ContentCreateUrl), name="add_content_url"),

    path('json_screen/<uuid:token_screen>', views.json_screen, name='json_screen'),  # NoLoginRequired
    path('display/<uuid:token_screen>', views.display, name='display'),  # NoLoginRequired
    path('screen_monitoring_endpoint/', views.screen_monitoring_endpoint, name='screen_monitoring_endpoint'),
    # NoLoginRequired
]