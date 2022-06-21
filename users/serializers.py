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


# class ReadUserSerializer(serializers.ModelSerializer):
#   class Meta:
#     model = User
#     exclude = (
#       "groups", 
#       "user_permissions",
#       "password", 
#       "last_login", 
#       "is_superuser", 
#       "is_staff", 
#       "is_active",
#       "favs",
#       "date_joined",
#     )

# # 일일이 수동으로 작성하지 않고 자동으로 만들어주는 ModelSerializer 사용
# class WriteUserSerializer(serializers.ModelSerializer):

#   class Meta:
#     model = User
#     fields = (
#       "username",
#       "first_name",
#       "last_name",
#       "email"
#     )

#   # validate 함수
#   def validate_first_name(self, value):
#     print(value)
#     return value.upper() # 반드시 value나 data를 리턴해야함!

# Read/Write UserSerializer 하나로 합치기 (+ Create 기능 추가)
class UserSerializer(serializers.ModelSerializer):
  # password 필드 users/me/에서 보여지지 않도록 설정
  password = serializers.CharField(write_only=True) # (serializer에게 이것을 write할 수 있게 알려줌?)

  class Meta:
    model = User
    fields = (
      "id", 
      "username", 
      "first_name", 
      "last_name", 
      "email",
      "avatar", 
      "superhost",
      "password", # 여기 field가 있으면 field가 보여지는 형태도 바꿀 수 있음!(validated_data에도 등장!)
    )
    read_only_fields = ("id", "superhost", "avatar")

  def validate_first_name(self, value):
    return value.upper()
  
  # ModelSerializer에서 제공하는 create 메서드 사용
  def create(self, validated_data):
    # print(validated_data)
    password = validated_data.get('password')
    # 생성된 유저 가져옴(password 설정 위해)
    user = super().create(validated_data)
    # models.User의 set_password 메서드 사용
    user.set_password(password)
    user.save()
    return user
