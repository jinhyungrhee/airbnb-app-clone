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

# 2. Create Room, Update Room에 사용되는 serializer ()
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

  # 2-1. create method 적용
  def create(self, validated_data):
    # print(validated_data)
    # create method는 항상 object instance를 return 해야 함
    return Room.objects.create(**validated_data) # unpacking vaildated data

  # 2-2. custom validation 적용
  # (1) validate_field 사용 (특정 필드에 대해서만 validate 진행)
  '''
  def validate_beds(self, beds):
    if beds < 5:
      raise serializers.ValidationError("Your house is too small")
    else:
      # 반드시 return을 해줘야 validated_data에 나타나게 됨!
      return beds
  '''
  # (2) validate 사용 (모든 object들을 validate함)
  # 하나가 다른 것에 의존하는 관계에서 사용, 모든 데이터에 대한 접근을 허용함.
  def validate(self, data):
    # 새로운 object 생성시(create)에만 해당 유효성검사를 진행하도록 로직 설계
    # (경우1) serializer에 instance가 있다면 update 진행
    if self.instance:
      check_in = data.get("check_in", self.instance.check_in) # 두 번째 파라미터로 default값 지정
      check_out = data.get("check_out", self.instance.check_out)
    # (경우2) serailizer에 instance가 없다면 create 진행
    else:
      check_in =  data.get("check_in")
      check_out = data.get("check_out")
    if check_in == check_out:
        raise serializers.ValidationError("Not enough time between changes")
    return data # 반드시 return을 해줘야 validated_data에 나타남

  # 2-3. update method 적용
  # instance 필요 : DRF가 update인지 create인지 구분하기 위해
  def update(self, instance, validated_data):
    # 우선 validated_data에서 가져오기
    instance.name = validated_data.get("name", instance.name) # 값이 없는 경우 default 값(instance.field == 현재값)
    instance.address = validated_data.get("address", instance.address)
    instance.price = validated_data.get("price", instance.price)
    instance.beds = validated_data.get("beds", instance.beds)
    instance.lat = validated_data.get("lat", instance.lat)
    instance.lng = validated_data.get("lng", instance.lng)
    instance.bedrooms = validated_data.get("bedrooms", instance.bedrooms)
    instance.bathrooms = validated_data.get("bathrooms", instance.bathrooms)
    instance.check_in = validated_data.get("check_in", instance.check_in)
    instance.check_out = validated_data.get("check_out", instance.check_out)
    instance.instant_book = validated_data.get("instant_book", instance.instant_book)
    instance.save()
    return instance # 항상 instance를 return해야 함

'''
# 2.See Room에 사용될 serializer
class BigRoomSerializer(serializers.ModelSerializer):

  class Meta:
    model = Room
    exclude = () # fields = ("__all__")
'''