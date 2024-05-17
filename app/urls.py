from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    AnnouncementListView, AnnouncementDetailView, AnnouncementCreateView, 
    AnnouncementUpdateView, ResponseCreateView, UserResponsesListView,
    ResponseDeleteView, ResponseAcceptView, CategoryListView, profile_view, 
    register_user, confirm_email, vote
)
from app import views

urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('announcement/<int:pk>/respond/', ResponseCreateView.as_view(), name='response_create'),
    path('confirm-email/<uidb64>/<token>/', confirm_email, name='confirm_email'),
    path("<int:question_id>/vote/", vote, name="vote"),
    path('', AnnouncementListView.as_view(), name='announcement-list'),
    path('announcement/<int:pk>/', AnnouncementDetailView.as_view(), name='announcement-detail'),
    path('announcement/create/', AnnouncementCreateView.as_view(), name='announcement-create'),
    path('announcement/<int:pk>/update/', views.AnnouncementUpdateView.as_view(), name='announcement_update'),
    path('announcement/<int:announcement_id>/response/', ResponseCreateView.as_view(), name='response-create'),
    path('user/responses/', UserResponsesListView.as_view(), name='user-responses'),
    path('response/<int:pk>/delete/', ResponseDeleteView.as_view(), name='response-delete'),
    path('response/<int:pk>/accept/', ResponseAcceptView.as_view(), name='response-accept'),
    path('ad/<int:ad_id>/edit/', views.edit_ad, name='edit_ad'),
    path('categories/', CategoryListView.as_view(), name='categories_list'),
    path('ad/<int:ad_id>/', views.ad_detail, name='ad_detail'),
    path('ad/<int:ad_id>/response/', views.create_response, name='create_response'),
    path('profile/', profile_view, name='profile'),
    path('announcement/<int:ad_id>/respond/', views.ResponseCreateView.as_view(), name='response-create'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
