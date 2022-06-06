from rest_framework import serializers
from users.serializers import UserSerializer
from .models import Room

'''
class RoomSerializer(serializers.Serializer):
  # 모델의 어떤 필드를 파이썬 객체에서 JSON으로 바꿔줄지 지정
  name = serializers.CharField(max_length=140)
  price = serializers.IntegerField()
  bedrooms = serializers.IntegerField()
  instant_book = serializers.BooleanField()
'''

# 1.List Rooms, See Room에 사용되는 serializer (간단하게 ModelSerializer 사용)
class ReadRoomSerializer(serializers.ModelSerializer):
  # user 세부정보를 가져오기 위해 UserSerializer 사용
  user = UserSerializer()

  class Meta:
    model = Room
    # [fields] : serializer에서 보여줄 필드 지정
    # fields = ("pk", "name", "price", "user")
    # [exclude] : serializer에서 제외할 필드 지정
    exclude = ("modified",)

# 2. Create Room에 사용되는 serializer ()
class WriteRoomSerializer(serializers.Serializer):
  # 유저들이 Room 모델에서 어떤 것을 전송할 수 있게 만드는 것이 좋을 지 고려
  # ModelSerializer가 자동으로 해주는 것을 수동으로 적어준 것
  name = serializers.CharField(max_length=140)
  address = serializers.CharField(max_length=140)
  price = serializers.IntegerField()
  beds = serializers.IntegerField(default=1)
  lat = serializers.DecimalField(max_digits=10, decimal_places=6)
  lng = serializers.DecimalField(max_digits=10, decimal_places=6)
  bedrooms = serializers.IntegerField(default=1)
  bathrooms = serializers.IntegerField(default=1)
  check_in = serializers.TimeField(default="00:00:00")
  check_out = serializers.TimeField(default="00:00:00")
  instant_book = serializers.BooleanField(default=False)

  # create method 적용
  def create(self, validated_data):
    # print(validated_data)
    # create method는 항상 object instance를 return 해야 함
    return Room.objects.create(**validated_data) # unpacking vaildated data


'''
# 2.See Room에 사용될 serializer
class BigRoomSerializer(serializers.ModelSerializer):

  class Meta:
    model = Room
    exclude = () # fields = ("__all__")
'''