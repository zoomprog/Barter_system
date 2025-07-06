from django.urls import path
from . import views
from .views import SignUpView

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.index, name='search'),  # Альтернативный URL для поиска
    # динамический параметр, который принимает целое число
    path('ad/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('ad/<int:pk>/edit/', views.edit_ad, name='edit_ad'),
    path('ad/<int:pk>/delete/', views.delete_ad, name='delete_ad'),
    path('create_ad/', views.create_ad, name='create_ad'),
    path('signup/', SignUpView.as_view(), name='signup'),
    
    # Предложения обмена
    path('proposals/', views.my_proposals, name='my_proposals'),
    path('proposal/<int:pk>/', views.proposal_detail, name='proposal_detail'),
    path('proposal/<int:pk>/update/', views.update_proposal_status, name='update_proposal_status'),
    path('proposal/<int:pk>/delete/', views.delete_proposal, name='delete_proposal'),
]