from rest_framework.serializers import ModelSerializer


from .models import UserModel


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "name", "surname"]


class LoginSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["email", "password"]


class MyInfoSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "name", "surname", "email", "age", "image"]


class UserCreateSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "name", "surname", "age", "email", "password"]

    def create(self, validated_data):
        return super().create(validated_data)


class VerifyStudent(ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["otp"]
