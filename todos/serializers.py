from rest_framework.serializers import ModelSerializer


from .models import TodoModel
from users.serializers import UserProfileSerializer


class TodoModelSerializer(ModelSerializer):
    user_id = UserProfileSerializer()

    class Meta:
        model = TodoModel
        fields = ["id", "title", "created_at", "deadline", "user_id"]


class TodoRertrieveSerializer(ModelSerializer):
    class Meta:
        model = TodoModel
        fields = "__all__"


class TodoCreateSerizalizer(ModelSerializer):
    class Meta:
        model = TodoModel
        fields = ["title", "deadline", "is_urgent"]

    def create(self, validated_data):
        user = self.context["request"].user
        return TodoModel.objects.create(user_id=user, **validated_data)


class TodoEditSerializer(ModelSerializer):
    class Meta:
        model = TodoModel
        fields = ["title", "deadline"]
