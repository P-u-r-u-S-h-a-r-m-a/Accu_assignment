from rest_framework import serializers
from users.models import *
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)
    confirm_password=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=['email','name','password','confirm_password']

    def validate(self,attrs):
        password=attrs.get('password')
        confirm_password=attrs.get('confirm_password')

        if (password!= confirm_password):
            raise serializers.ValidationError("Both passwords should match.")
        return attrs

    def validate_email(self,value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('user with similar email already exists')
        return value
    
    def create(self,validated_data):
        user=User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
        )
        #user.is_active(True)
        user.save()
        return user




class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class FriendRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model=FriendRequest
        fields=['sender','receiver','status','created_at']
