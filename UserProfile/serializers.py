from rest_framework import serializers
import datetime

from follow.serializers import FollowSerializer
from .models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'gender',
                  'date_of_birth', 'password', 'confirm_password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_date_of_birth(self, value):
        today = datetime.date.today()
        age = today.year - value.year - \
            ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError(
                'You must be at least 18 years old to register')
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match')
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            gender=validated_data['gender'],

            date_of_birth=validated_data['date_of_birth'],
            password=validated_data['password']
        )
        return user


class UserPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True)
    new_password = serializers.CharField(max_length=128, write_only=True)

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Incorrect old password.')
        return value

    def validate_new_password(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Password is too short.")
        else:
            return value


class UserProfileSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ('id','email', 'first_name', 'last_name', 'date_of_birth', 'gender',
                  'profile_pic', 'about_me', 'post_count', 'followers_count', 'following_count', 'following')

    def get_post_count(self, obj):
        return obj.get_post_count()

    def get_followers_count(self, obj):
        return obj.get_followers_count()

    def get_following_count(self, obj):
        return obj.get_following_count()
    
    def get_following(self, obj):
        return obj.following.values_list('id', flat=True)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'profile_pic', 'about_me',)

class ChangePasswordSerializer(serializers.Serializer):
    model = CustomUser
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is not registered.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match.')
        if len(data['new_password']) < 5:
            raise serializers.ValidationError('Password is too Short. ')
        return data



class FollowSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source='user', read_only=True)
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'user_profile', 'is_following')

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(pk=request.user.pk).exists()
        return False 

