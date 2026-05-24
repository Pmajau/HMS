from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    UserSerializer, RegisterSerializer,
    ChangePasswordSerializer, UpdateProfileSerializer
)
from .permissions import IsAdmin

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Admin-only: create new user accounts"""
    serializer_class    = RegisterSerializer
    permission_classes  = [IsAdmin]


class LoginView(APIView):
    """Public: login with email + password, returns JWT tokens"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from django.contrib.auth import authenticate
        email    = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'Account is deactivated. Contact admin.'},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user':    UserSerializer(user).data
        })


class LogoutView(APIView):
    """Blacklists the refresh token on logout"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully'})
        except Exception:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get or update the currently logged-in user's profile"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateProfileSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """Change password for the logged-in user"""
    serializer_class   = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password changed successfully'})


class UserListView(generics.ListAPIView):
    """Admin-only: list all users with optional role filter"""
    serializer_class   = UserSerializer
    permission_classes = [IsAdmin]
    queryset           = User.objects.all()
    filterset_fields   = ['role', 'is_active']
    search_fields      = ['email', 'first_name', 'last_name']


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Admin-only: view or edit any user account"""
    serializer_class   = UserSerializer
    permission_classes = [IsAdmin]
    queryset           = User.objects.all()

    def patch(self, request, *args, **kwargs):
        """Allow admin to deactivate/reactivate accounts"""
        return super().partial_update(request, *args, **kwargs)