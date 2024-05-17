from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    AnnouncementListView, AnnouncementDetailView, AnnouncementCreateView, 
    AnnouncementUpdateView, ResponseCreateView, UserResponsesListView,
    ResponseDeleteView, ResponseAcceptView, CategoryListView, 
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
    path('categories/', CategoryListView.as_view(), name='categories_list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
