from django.urls import path

from .views import *
urlpatterns = [
    path('csrf_cookie/',GETCSRFToken.as_view(),name='csrf_cookie'),
     path('signup/', Signup.as_view(), name='signup'),
     path('login/',LoginView.as_view(),name='login'),
     path('logout/',LogoutView.as_view(),name='logout'),
     path('users/search/', SearchUserView.as_view(), name='search_user'),
     path('friend-requests/send/', SendFriendRequestView.as_view(), name='send-friend-request'),
     path('friend-requests/view/',FriendRequestView.as_view(),name='friend-request-view'),
     path('friend-requests/response/',RespondFriendRequestView.as_view(),name='friend-request-response'),
     path('user/friends/', FriendListView.as_view(), name='friend-list'),
 ]
