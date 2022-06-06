from rest_framework import serializers
from .models import User

# user에 관한 추가정보를 얻기 위한 serializer
class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    # fields = ("username", "superhost")
    exclude = (
      "groups", 
      "user_permissions",
      "password", 
      "last_login", 
      "is_superuser", 
      "is_staff", 
      "is_active", 
      "date_joined",
      "favs"
    )