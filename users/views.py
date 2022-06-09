from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from rooms.serializers import RoomSerializer
from rooms.models import Room
from .models import User
from .serializers import ReadUserSerializer, WriteUserSerializer

class MeView(APIView):
  
  # permission_classes를 사용하면 'if request.user.is_authenticated:'사용하지 않아도 됨!
  # 해당 class 전체에 모두 적용됨
  # Function Based View에서는 @permission_classes([IsAuthenticated])의 데코레이터 추가하여 사용
  permission_classes = [IsAuthenticated]


  def get(self, request):
    # if request.user.is_authenticated: # is_authenticated()로 하면 'bool' object is not callable 에러 발생!
    return Response(ReadUserSerializer(request.user).data)

  # pk를 입력받으면 너가 해당 유저인지 체크하고 맞으면 profile update해줌
  def put(self, request):
    serializer = WriteUserSerializer(request.user, data=request.data, partial=True) # request.user가 반드시 들어가야함!
    # print(serializer.is_valid()) # True
    if serializer.is_valid():
      serializer.save()
      return Response()
    else:
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 나의 위치를 파악하기 위해서 call할 수 있는 URL이 필요함(로그인하면 id를 알 수 없음) -> 함수를 분리한 이유
# 작은 기능은 함수형 뷰(api_view) 사용
@api_view(["GET"])
def user_detail(request, pk):
  try:
    user = User.objects.get(pk=pk)
    return Response(ReadUserSerializer(user).data)
  except User.DoesNotExist:
    return Response(status=status.HTTP_404_NOT_FOUND)

# fav를 추가하는 기능

class FavsView(APIView):

  permission_classes = [IsAuthenticated]

  def get(self, request):
    user = request.user
    serializer = RoomSerializer(user.favs.all(), many=True).data
    return Response(serializer)


  # 해당 뷰에서는 어떠한 기록을 생성하지 않고 업데이트만 진행함
  def put(self, request):
    pk = request.data.get("pk", None)
    user = request.user
    if pk is not None:
      # 해당 room 찾기
      try:
        room = Room.objects.get(pk=pk)
        # 만약 찾은 room이 user의 favs 리스트 안에 존재한다면 delete
        if room in user.favs.all():
          user.favs.remove(room)
        # 만약 찾은 room이 user의 favs 리스트 안에 없다면 추가
        else:
          user.favs.add(room)
        return Response()
      except Room.DoesNotExist:
        pass
    return Response(status=status.HTTP_400_BAD_REQUEST)
