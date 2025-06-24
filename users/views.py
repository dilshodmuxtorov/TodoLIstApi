from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.core.mail import send_mail
from django.conf import settings


from .models import UserModel
from .authentication import CustomUserJWTAuthentication
from .serializers import (
    LoginSerializer,
    MyInfoSerializer,
    UserCreateSerializer,
    VerifyStudent,
)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_summary="Foydalanuvchi login qilish",
        operation_description="""
Foydalanuvchi `email` va `parol` bilan login qilsa, unga JWT `access_token`
va `refresh_token` qaytariladi.
Agar maʼlumotlar noto‘g‘ri bo‘lsa, 401 yoki 400 xato kodi qaytariladi.
        """,
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Tokenlar qaytarildi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "refresh_token": openapi.Schema(type=openapi.TYPE_STRING),
                        "access_token": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: openapi.Response(
                description="Validatsiya xatoliklari",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"errors": openapi.Schema(type=openapi.TYPE_OBJECT)},
                ),
            ),
            401: openapi.Response(
                description="Login maʼlumotlari noto‘g‘ri",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Invalid email or password",
                        )
                    },
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            try:
                user = UserModel.objects.get(email=email)
            except UserModel.DoesNotExist:
                return Response(
                    {"error": "Invalid email or password"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if not user.check_password(password):
                return Response(
                    {"error": "Invalid email or password"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            refresh_token = RefreshToken.for_user(user)
            access_token = refresh_token.access_token

            return Response(
                {
                    "refresh_token": str(refresh_token),
                    "access_token": str(access_token),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )


class MyInfoView(APIView):
    authentication_classes = [CustomUserJWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Foydalanuvchi o‘z ma’lumotlarini olish",
        operation_description="""
Ushbu endpoint orqali avtorizatsiyadan o'tgan foydalanuvchi
o‘zining ma’lumotlarini olishi mumkin.
        """,
        responses={
            200: openapi.Response(
                description="Foydalanuvchi ma’lumotlari",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                        ),
                        "full_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "created_at": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                        ),
                        "updated_at": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                        ),
                    },
                ),
            ),
            404: openapi.Response(
                description="Foydalanuvchi topilmadi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING, example="User not found"
                        )
                    },
                ),
            ),
            401: openapi.Response(description="Token noto‘g‘ri yoki mavjud emas"),
        },
    )
    def get(self, request):
        user_id = request.user.id

        try:
            user = UserModel.objects.get(id=user_id)
            serializer = MyInfoSerializer(instance=user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UserCreateView(APIView):

    @swagger_auto_schema(
        operation_summary="Yangi foydalanuvchini ro'yxatdan o'tkazish",
        operation_description="""
Ushbu endpoint orqali foydalanuvchi ro'yxatdan o'tadi. Ro'yxatdan o'tgach,
foydalanuvchiga email orqali `otp` yuboriladi.
Shuningdek, JWT tokenlar (`access` va `refresh`) qaytariladi.
        """,
        request_body=UserCreateSerializer,
        responses={
            200: openapi.Response(
                description="Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "refresh_token": openapi.Schema(type=openapi.TYPE_STRING),
                        "access_token": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: openapi.Response(
                description="Validatsiya xatosi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING),
                        "details": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
        },
    )
    def post(self, request):
        serializer = UserCreateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            user = serializer.instance
            otp = user.otp
            email = user.email

            send_mail(
                subject="Verification Code",
                message=f"Your verification code is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            refresh_token = RefreshToken.for_user(user)
            access_token = refresh_token.access_token

            return Response(
                {
                    "refresh_token": str(refresh_token),
                    "access_token": str(access_token),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Mistake on serializer", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class VerifyUserView(APIView):
    authentication_classes = [CustomUserJWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Foydalanuvchini OTP orqali faollashtirish",
        operation_description="""
Foydalanuvchi ro'yxatdan o'tgach yuborilgan OTP kodni shu endpoint orqali kiritadi.
Agar kod to'g'ri bo'lsa, `is_active=True` bo'ladi va foydalanuvchi faollashadi.
Agar noto‘g‘ri kiritilsa, foydalanuvchi o‘chiriladi.
        """,
        request_body=VerifyStudent,
        responses={
            200: openapi.Response(
                description="Foydalanuvchi faollashtirildi yoki xato OTP yuborildi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Activated successfully"
                        ),
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Otp is not correct"
                        ),
                    },
                ),
            ),
            404: openapi.Response(
                description="Foydalanuvchi topilmadi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING, example="User not found"
                        )
                    },
                ),
            ),
            401: openapi.Response(description="Avtorizatsiya xatosi"),
        },
    )
    def post(self, request):
        otp = request.data.get("otp")
        user_id = request.user.id

        try:
            user = UserModel.objects.get(id=user_id)
            if user.otp == str(otp):
                user.is_active = True
                user.otp = ""
                user.save()
                return Response(
                    {"message": "Activated successfully"}, status=status.HTTP_200_OK
                )
            else:
                user.delete()
                return Response(
                    {"error": "Otp is not correct"}, status=status.HTTP_200_OK
                )
        except UserModel.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
