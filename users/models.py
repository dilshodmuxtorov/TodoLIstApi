import random
from django.db import models
from django.core.exceptions import ValidationError


def validate_password(value: str):
    if len(value) < 8:
        raise ValidationError("Password should be at least 8 character")
    else:
        for i in value:
            if i.isdigit():
                return
        raise ValidationError("Password should contain numbers")


def create_otp():
    return str(random.randint(10000, 99999))


class UserModel(models.Model):
    name = models.CharField(max_length=255, default="")
    surname = models.CharField(max_length=255, default="")
    age = models.IntegerField(default=0)
    email = models.EmailField()
    password = models.CharField(
        max_length=64,
        default="",
        validators=[
            validate_password,
        ],
    )
    image = models.ImageField(upload_to="user/", null=True, blank=True, default="")
    otp = models.CharField(max_length=5, default=create_otp())
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = ["email"]

    class Meta:
        db_table = "users"
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    def __str__(self):
        return self.name + " " + self.surname
