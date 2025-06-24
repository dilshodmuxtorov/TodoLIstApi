from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import TodoModel
from users.authentication import CustomUserJWTAuthentication
from .serializers import (
    TodoModelSerializer,
    TodoRertrieveSerializer,
    TodoCreateSerizalizer,
    TodoEditSerializer,
)


class TodoListView(APIView):
    authentication_classes = [CustomUserJWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Foydalanuvchining barcha todolarini olish",
        operation_description="Bu endpoint login bo‘lgan foydalanuvchining "
        "barcha todolarini qaytaradi."
        "Har bir todo elementda sarlavha, tavsif va tugallanganlik holati bo'ladi.",
        responses={
            200: openapi.Response(
                description="Foydalanuvchining todolari muvaffaqiyatli olindi",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(
                                type=openapi.TYPE_INTEGER, description="Todo IDsi"
                            ),
                            "title": openapi.Schema(
                                type=openapi.TYPE_STRING, description="Todo sarlavhasi"
                            ),
                            "description": openapi.Schema(
                                type=openapi.TYPE_STRING, description="Todo tavsifi"
                            ),
                            "is_completed": openapi.Schema(
                                type=openapi.TYPE_BOOLEAN,
                                description="Todo bajarilganmi",
                            ),
                            "created_at": openapi.Schema(
                                type=openapi.FORMAT_DATETIME,
                                description="Yaratilgan vaqt",
                            ),
                            "updated_at": openapi.Schema(
                                type=openapi.FORMAT_DATETIME,
                                description="Yangilangan vaqt",
                            ),
                        },
                    ),
                ),
            ),
            401: openapi.Response(description="Token mavjud emas yoki noto‘g‘ri"),
        },
    )
    def get(self, request):
        user = self.request.user
        todos = TodoModel.objects.filter(user_id=user)
        serializer = TodoModelSerializer(todos, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class TodoRetrieveView(APIView):
    authentication_classes = [CustomUserJWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Bitta todo ma'lumotini olish",
        operation_description="""
Ushbu endpoint orqali foydalanuvchi o'ziga tegishli bitta
todo yozuvini `pk` bo‘yicha olishi mumkin.
Agar todo topilmasa yoki foydalanuvchiga tegishli bo‘lmasa, 404 xato qaytariladi.
        """,
        responses={
            200: openapi.Response(
                description="Todo muvaffaqiyatli topildi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="Todo IDsi"
                        ),
                        "title": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Todo sarlavhasi"
                        ),
                        "description": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Todo tavsifi"
                        ),
                        "is_completed": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN, description="Bajarilganmi"
                        ),
                        "created_at": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                            description="Yaratilgan vaqt",
                        ),
                        "updated_at": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                            description="Yangilangan vaqt",
                        ),
                    },
                ),
            ),
            404: openapi.Response(
                description="Todo topilmadi yoki sizga tegishli emas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Does not exist or not authenticated",
                        )
                    },
                ),
            ),
            401: openapi.Response(description="Token noto'g'ri yoki mavjud emas"),
        },
    )
    def get(self, request, pk):
        user_id = self.request.user
        try:
            todo = TodoModel.objects.get(pk=pk, user_id=user_id)
            serializer = TodoRertrieveSerializer(todo)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except TodoModel.DoesNotExist:
            return Response(
                data={"error": "Does not exist or not authenticated"},
                status=status.HTTP_404_NOT_FOUND,
            )


class IsFinishedSetTrueView(APIView):
    authentication_classes = [CustomUserJWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Todo ni bajarilgan deb belgilash",
        operation_description="""
Ushbu endpoint `pk` orqali yuborilgan todo-ni `is_finished=True` qilib belgilaydi.
Faqat foydalanuvchining o‘ziga tegishli todo-larga ruxsat beriladi.
        """,
        responses={
            200: openapi.Response(
                description="Todo muvaffaqiyatli bajarilgan deb belgilandi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Todo is finished"
                        )
                    },
                ),
            ),
            404: openapi.Response(
                description="Todo topilmadi yoki sizga tegishli emas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Todo does not exist or unauthorized",
                        )
                    },
                ),
            ),
            401: openapi.Response(description="Avtorizatsiya xatosi"),
        },
    )
    def patch(self, request, pk):
        user_id = self.request.user
        try:
            todo = TodoModel.objects.get(pk=pk, user_id=user_id)
            todo.is_finished = True
            todo.save()
            return Response(
                data={"message": "Todo is finished"}, status=status.HTTP_200_OK
            )
        except TodoModel.DoesNotExist:
            return Response(
                data={"error": "Todo does not exist or unauthorized"},
                status=status.HTTP_404_NOT_FOUND,
            )


class TodoCreateView(APIView):
    authentication_classes = [CustomUserJWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Yangi todo yaratish",
        operation_description="""
Ushbu endpoint orqali avtorizatsiyadan o'tgan foydalanuvchi yangi todo yaratishi mumkin.
Kerakli maydonlar: `title`, `description` (ixtiyoriy), `is_finished` (default: False).
        """,
        request_body=TodoCreateSerizalizer,
        responses={
            201: openapi.Response(
                description="Todo muvaffaqiyatli yaratildi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "title": openapi.Schema(type=openapi.TYPE_STRING),
                        "description": openapi.Schema(type=openapi.TYPE_STRING),
                        "is_finished": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "created_at": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                        ),
                        "updated_at": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Validatsiya xatosi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Mistake on serializer"
                        ),
                        "details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(
                                type=openapi.TYPE_STRING
                            ),
                        ),
                    },
                ),
            ),
            401: openapi.Response(description="Token noto‘g‘ri yoki mavjud emas"),
        },
    )
    def post(self, request):
        serializer = TodoCreateSerizalizer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "Mistake on serializer", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class DeleteApiView(APIView):
    authentication_classes = [CustomUserJWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Todo ni o‘chirish",
        operation_description="""
Foydalanuvchining o‘ziga tegishli todo elementni `pk` orqali o‘chiradi.
Agar todo mavjud bo‘lmasa yoki boshqa foydalanuvchiga tegishli bo‘lsa, 404 qaytariladi.
        """,
        responses={
            200: openapi.Response(
                description="Muvaffaqiyatli o‘chirildi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Deleted successfully"
                        )
                    },
                ),
            ),
            404: openapi.Response(
                description="Todo topilmadi yoki foydalanuvchiga tegishli emas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="""Does not exist or the object
                            does not belong to the user""",
                        )
                    },
                ),
            ),
            401: openapi.Response(description="Avtorizatsiya xatosi"),
        },
    )
    def delete(self, request, pk):
        user_id = request.user.id

        try:
            todo = TodoModel.objects.get(user_id=user_id, pk=pk)
            todo.delete()
            return Response(
                data={"message": "Deleted successfully"}, status=status.HTTP_200_OK
            )
        except TodoModel.DoesNotExist:
            return Response(
                data={
                    "error": "Does not exist or the object does not belong to the user"
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class EditTodoApiView(APIView):
    authentication_classes = [CustomUserJWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Todo-ni tahrirlash",
        operation_description="""
Ushbu endpoint orqali foydalanuvchi o'ziga tegishli todo yozuvini yangilashi mumkin.
`title` va `deadline` maydonlari yuborilishi kerak.
        """,
        request_body=TodoEditSerializer,
        responses={
            200: openapi.Response(
                description="Todo muvaffaqiyatli tahrirlandi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Edited"
                        )
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
            404: openapi.Response(
                description="Todo topilmadi yoki sizga tegishli emas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="""Does not exist or the object
                            does not belong to the user""",
                        )
                    },
                ),
            ),
            401: openapi.Response(description="Token noto‘g‘ri yoki mavjud emas"),
        },
    )
    def put(self, request, pk):
        user_id = request.user.id

        try:
            todo = TodoModel.objects.get(user_id=user_id, pk=pk)
        except TodoModel.DoesNotExist:
            return Response(
                data={
                    "error": "Does not exist or the object does not belong to the user"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TodoEditSerializer(instance=todo, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(data={"message": "Edited"}, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"error": "Mistake on serializer", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
