from django.urls import path
from . import views

urlpatterns = [
    path('',                views.NotificationListView.as_view(),    name='notifications'),
    path('unread/',         views.UnreadNotificationsView.as_view(),  name='unread_notifications'),
    path('unread/count/',   views.UnreadCountView.as_view(),          name='unread_count'),
    path('mark-all-read/',  views.MarkAllReadView.as_view(),          name='mark_all_read'),
    path('<int:pk>/read/',  views.MarkNotificationReadView.as_view(), name='mark_read'),
]