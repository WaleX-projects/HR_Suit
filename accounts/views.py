from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.utils import generate_verification_token, confirm_verification_token
from accounts.serializers import UserSerializer,RegisterSerializer
#from companies.models import Company 
User = get_user_model()

# -----------------------------
# REGISTER / SIGNUP
# -----------------------------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.mail import send_mail


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print("Incoming data:", request.data)

        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = serializer.save()

            frontend_url = "https://thesuit.netlify.app"
            #generate token base on user's id and email
            token = generate_verification_token(user.email)
            
            verify_url = f"{frontend_url}/verify-account/{token}"
            send_mail(
                "Verify Your Email",
                f"Click this link to verify your account: {verify_url}",
                "noreply@Thesuite.com",
                [user.email],
            )

            return Response(
                {"message": "User created. Check your email to verify."},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print("ERROR:", str(e))
            return Response(
                {"error": "Something went wrong", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
# -----------------------------
# EMAIL VERIFICATION
# -----------------------------
class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        email = confirm_verification_token(token)
        if not email:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(email=email)
        if user.is_verified:
            return Response({"message": "Email already verified"}, status=status.HTTP_200_OK)

        user.is_verified = True
        user.save()
        return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)


# -----------------------------
# LOGIN (JWT)
# -----------------------------
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = User.objects.filter(email=email).first()
        if user is None or not user.check_password(password):
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_verified:
            return Response({"error": "Email not verified"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            "message":f"login successfully, welcome {user.first_name}",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)


# -----------------------------
# PROFILE VIEW
# -----------------------------
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -----------------------------
# PASSWORD RESET REQUEST
# -----------------------------
class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        token = generate_verification_token(user.email)
        reset_path = f"/api/accounts/reset-password/{token}/"
        reset_url = request.build_absolute_uri(reset_path)

        send_mail(
    "Password Reset",
    f"Click this link to reset your password: {reset_url}",
    "noreply@hrsaas.com",
    [user.email]
        )

        return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)


# -----------------------------
# PASSWORD RESET
# -----------------------------
class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        email = confirm_verification_token(token)
        if not email:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        password = request.data.get("password")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)