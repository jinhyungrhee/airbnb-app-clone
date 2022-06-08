from rest_framework import serializers
from .models import User

# user에 관한 추가정보를 얻기 위한 serializer(오직 relationship을 위해서 사용됨)
class RelatedUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = (
      "username", 
      "first_name",
      "last_name",
      "email",
      "avatar",
      "superhost",
    )


class ReadUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    exclude = (
      "groups", 
      "user_permissions",
      "password", 
      "last_login", 
      "is_superuser", 
      "is_staff", 
      "is_active", 
      "date_joined",
    )