from django.urls import path
from . import views
from .views import SignUpView

urlpatterns = [
    path('', views.index, name='index'),
    # динамический параметр, который принимает целое число
    path('ad/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('ad/<int:pk>/edit/', views.edit_ad, name='edit_ad'),
    path('ad/<int:pk>/delete/', views.delete_ad, name='delete_ad'),
    path('create_ad/', views.create_ad, name='create_ad'),
    path('signup/', SignUpView.as_view(), name='signup'),

]