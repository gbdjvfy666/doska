from django.urls import path
from .views import (
    AnnouncementListView, AnnouncementDetailView, AnnouncementCreateView, 
    AnnouncementUpdateView, ResponseCreateView, UserResponsesListView,
    ResponseDeleteView, AcceptResponseView, CategoryListView
)

urlpatterns = [
    path('', AnnouncementListView.as_view(), name='announcement-list'),
    path('announcement/<int:pk>/', AnnouncementDetailView.as_view(), name='announcement-detail'),
    path('announcement/create/', AnnouncementCreateView.as_view(), name='announcement-create'),
    path('announcement/<int:pk>/update/', AnnouncementUpdateView.as_view(), name='announcement-update'),
    path('announcement/<int:announcement_id>/response/', ResponseCreateView.as_view(), name='response-create'),
    path('user/responses/', UserResponsesListView.as_view(), name='user-responses'),
    path('response/<int:pk>/delete/', ResponseDeleteView.as_view(), name='response-delete'),
    path('response/<int:pk>/accept/', AcceptResponseView.as_view(), name='response-accept'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
]