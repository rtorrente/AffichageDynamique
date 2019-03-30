from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    # General
    path('', login_required(views.home), name='home'),

    # Content
    path('content/list/<int:pk>', login_required(views.content_list), name='content_list'),
    path('content/moderate/list/<int:pk>', login_required(views.content_list_moderate), name='content_list_moderate'),
    path('content/moderate/home', login_required(views.moderation_home), name='moderation_home'),
    path('content/view/<int:pk>', login_required(views.content_view), name='content_view'),
    path('content/approve/<int:pk>', login_required(views.approve_content), name='approve_content'),
    path('content/reject/<int:pk>', login_required(views.reject_content), name='reject_content'),
    path('content/delete/<int:pk>', login_required(views.delete_content), name='delete_content'),
    path('content/add/image/', login_required(views.content_create_image), name="add_content_image"),
    path('content/add/youtube/', login_required(views.content_create_youtube), name="add_content_youtube"),
    path('content/add/url', login_required(views.content_create_url), name="add_content_url"),

    # Extra
    path('extra/restaurants', login_required(views.restaurant_add), name="add_restaurant"),

    # Screen
    path('screen/list/', login_required(views.list_screen), name='list_screen'),
    path('screen/view/<int:pk_screen>', login_required(views.view_screen), name='view_screen'),
    path('screen/monitoring/', login_required(views.screen_monitoring), name='screen_monitoring'),

    # Subscription
    path('subscription/delete/<int:pk_sub>', login_required(views.delete_subscription), name='delete_subscription'),
    path('subscription/add/<int:pk_screen>/<str:type_sub>', login_required(views.add_subscription),
         name='add_subscription'),
    path('subscription/up/<int:pk_sub>', login_required(views.up_subscription), name='up_subscription'),
    path('subscription/down/<int:pk_sub>', login_required(views.down_subscription), name='down_subscription'),

    # No Login
    path('screen/monitoring_get_control_mode/<str:token>', views.screen_monitoring_get_control_mode,
         name='screen_monitoring_get_control'),
    path('screen/json/<str:token_screen>', views.json_screen, name='json_screen'),
    path('display/<str:token_screen>', views.display, name='display'),
    path('screen/monitoring_endpoint/', views.screen_monitoring_endpoint, name='screen_monitoring_endpoint'),
]