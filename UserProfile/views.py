from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from django.db.models import Q, Count
from UserProfile.models import CustomUser
from follow.serializers import FollowSerializer
from .serializers import ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from .serializers import CustomUserSerializer, UserProfileSerializer, UserPasswordSerializer, UserProfileUpdateSerializer
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def generate_token(user):
    token_generator = PasswordResetTokenGenerator()
    return token_generator.make_token(user)
    
class UserRegistrationView(APIView):
    serializer_class = CustomUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            serializer = UserProfileSerializer(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': serializer.data
            })
        else:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'detail': 'Logout successful.'})


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request):
        user = request.user
        print(f"user is {user}")
        posts_count = user.posts.count()
        followers_count = user.followers.count()
        following_count = user.following.count()
        user.posts_count = posts_count
        user.followers_count = followers_count
        user.following_count = following_count
        serializer = self.serializer_class(user)
        return Response(serializer.data)


class UserProfileUpdateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileUpdateSerializer

    def put(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(
                serializer.validated_data['new_password'])
            request.user.save()
            return Response({'detail': 'Password updated successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            user_to_follow = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user == user_to_follow:
            return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.following.filter(pk=user_id).exists():
            return Response({'detail': 'You have already followed this user.'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.following.add(user_to_follow)
        request.user.following_count += 1
        user_to_follow.followers.add(request.user)
        user_to_follow.followers_count += 1

        request.user.save()
        user_to_follow.save()

        serializer = FollowSerializer(user_to_follow, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class FollowDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            user_to_unfollow = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user == user_to_unfollow:
            return Response({'detail': 'You cannot unfollow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.following.remove(user_to_unfollow)
        request.user.following_count -= 1
        user_to_unfollow.followers.remove(request.user)
        user_to_unfollow.followers_count -= 1

        request.user.save()
        user_to_unfollow.save()

        return Response({'detail': f'You have unfollowed {user_to_unfollow.email}.'}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self, queryset=None):
        obj = self.request.user
        return obj
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({
                    "old_password": ["Wrong password. "]
                }, status=status.HTTP_400_BAD_REQUEST)
            #set_password hashes password
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': "Password updated successfully"
                
            }
            
            return Response(response)
    

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if user is not None:
            token = generate_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            base_url = request.data.get('base_url')  # Assuming the base URL is sent from the frontend
            current_site = get_current_site(request)
            if base_url:
                # Set a default base URL if none is provided from the frontend
                reset_password_url = f"{base_url}/user/confirm-reset-password/{uidb64}/{token}"
            elif current_site:
                reset_password_path = reverse('confirm-reset-password', kwargs={'uidb64': uidb64, 'token': token})
                reset_password_url = f"{request.scheme}://{current_site.domain}{reset_password_path}"
            else:
                reset_password_url = f"https://journeyofmotherhood.org/user/confirm-reset-password/{uidb64}/{token}"

            subject = 'Reset Your Journey of Motherhood Password'
            message = f'Click the link below to reset your password: {reset_password_url}'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return Response({'detail': 'A reset password link has been sent to your email.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid email.'}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmResetPasswordView(APIView):
    def post(self, request, uidb64, token):
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.filter(pk=uid).first()

        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            serializer = ResetPasswordSerializer(data=request.data)
            if serializer.is_valid():
                new_password = serializer.validated_data['new_password']
                user.set_password(new_password)
                user.save()
                return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Invalid reset password link.'}, status=status.HTTP_400_BAD_REQUEST)

class TopUsersView(APIView):
    def get(self, request, format=None):
        queryset = CustomUser.objects.annotate(
            num_followers=Count('followers')
        ).annotate(
            num_following=Count('following')
        ).annotate(
            num_post=Count('posts')
        ).order_by('-post_count')[:10]
        serializer = CustomUserSerializer(queryset, many=True)
        return Response(serializer.data)

