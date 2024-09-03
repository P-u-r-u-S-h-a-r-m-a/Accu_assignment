from django.contrib.auth import authenticate,login,logout
from users.models import *
from django.db.models import Q
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from users.serializers import *
from django.views.decorators.csrf import ensure_csrf_cookie,csrf_protect
from django.utils.decorators import method_decorator
from django.conf import settings
from users.serializers import UserSerializer
from rest_framework.throttling import UserRateThrottle

class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class FriendRequestThrottle(UserRateThrottle):  #Limiting friend requests to 3 per minute
    rate = '3/minute'

@method_decorator(ensure_csrf_cookie,name='dispatch')
class GETCSRFToken(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        return Response({'success':'CSRF is set'})

@method_decorator(csrf_protect,name='dispatch')
class Signup(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer= UserSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.create(serializer.validated_data)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return Response({'detail': 'Logged in successfully.'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Account is inactive.'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Email or password is incorrect.'},
                            status=status.HTTP_400_BAD_REQUEST)

class SearchUserView(APIView):
    permission_classes=[IsAuthenticated]
    pagination_class=UserPagination

    def get(self,request):
        search_query = request.query_params.get('search', '').strip().lower()
        if not search_query:
            return Response({"detail": "Search query cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Querying to search by email or name exact email and contains name
        users=User.objects.filter(
            Q(email__iexact=search_query) | Q(name__icontains=search_query)
        )
        paginator = UserPagination()
        paginated_users = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)

class SendFriendRequestView(APIView):
    permission_classes=[IsAuthenticated]
    throttle_classes=[FriendRequestThrottle]

    def post(self,request):
        sender=request.user
        receiver_email=request.data.get('email')

        if(sender.email==receiver_email):
            return Response({'detail':'You cannot send friend request to yourself'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            receiver=User.objects.get(email=receiver_email)
        except User.DoesNotExist:
            return Response({'detail':'User does not Exist'},
                            status=status.HTTP_404_NOT_FOUND)
        # Checking if the users are already friends 
        if FriendRequest.objects.filter(
            (Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)) & 
            Q(status='accepted')
        ).exists():
            return Response({"detail": "You are already friends with this user."},
                            status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(sender=sender,receiver=receiver).exists():
            return Response ({'detail':'Friend request is already sent'},
                             status=status.HTTP_400_BAD_REQUEST)
        
        FriendRequest.objects.create(sender=sender,receiver=receiver)
        return Response({'detail':'Request is sent Successfully'},
                        status=status.HTTP_201_CREATED)

class FriendRequestView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        user=request.user
        received_requests=FriendRequest.objects.filter(receiver=user,status='pending') #received pending requests
        
        sent_requests=FriendRequest.objects.filter(sender=user,status='pending') #sent pending requests


        received_serializer=FriendRequestSerializer(received_requests,many=True)

        sent_serializer=FriendRequestSerializer(sent_requests,many=True)

        return Response({
            'received_requests':received_serializer.data,
            'sent_requests':sent_serializer.data
        })


class RespondFriendRequestView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        sender_email=request.data.get('sender')
        response=request.data.get('response')

        if not sender_email or response not in ['accept', 'reject']:
            return Response({'detail': "Plsease provide a valid email or response(eg accept or reject)"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            sender = User.objects.get(email=sender_email)
        except User.DoesNotExist:
            return Response({'detail': 'Sender not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            sender = User.objects.get(email=sender_email)
            friend_request=FriendRequest.objects.get(sender=sender,receiver=request.user,status='pending')
        except FriendRequest.DoesNotExist:
            return Response({'detail':'Friend Request Not Found'}
                            ,status=status.HTTP_404_NOT_FOUND)
        if response=='accept':
            friend_request.status='accepted'
            friend_request.save()
            return Response({'detail':"Friend Request Accepted"},
                            status=status.HTTP_200_OK)
        if response=='reject':
            friend_request.status='rejected'
            friend_request.save()
            return Response({'detail':"Friend Request Rejected"},
                            status=status.HTTP_200_OK)
        else:
            return Response({'detail':"Invalid Response"},
                status=status.HTTP_400_BAD_REQUEST)

class FriendListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        accepted_requests = FriendRequest.objects.filter(
            Q(sender=user, status='accepted') | 
            Q(receiver=user, status='accepted')
        )

        friends = []
        for friend_request in accepted_requests:
            if friend_request.sender == user:
                friends.append(friend_request.receiver)
            else:
                friends.append(friend_request.sender)
                
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    def post(self,request):
        logout(request)
        return Response({'detail':'User Logged out Successfully.'},
                        status=status.HTTP_200_OK)