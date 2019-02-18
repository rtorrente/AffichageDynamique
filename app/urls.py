from django.urls import path, include
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(views.Home.as_view()), name='home'),
    path('list_content/<int:pk>', views.content_list, name='content_list'),
]