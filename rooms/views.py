# from rest_framework.decorators import api_view # (1)함수형 뷰 사용
from rest_framework.views import APIView # (2)클래스형 뷰 사용
# from rest_framework.generics import ListAPIView, RetrieveAPIView # (3)제네릭 뷰 사용
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from .models import Room
from .serializers import RoomSerializer

# 1. ListRooms
# (1)함수형 뷰 사용 : api_view (제네릭뷰가 아니기 때문에 pagination 기능 X)
# [@api_view] : django가 views를 처리하는 방식을 바꿀 수 있음. 해당 뷰는 rest framework에서 처리됨.
'''
@api_view(["GET", "POST"])
def rooms_view(request):
  if request.method == "GET":
    rooms = Room.objects.all()[:5]
    serializer = ReadRoomSerializer(rooms, many=True).data
    return Response(serializer)
  elif request.method == "POST":
    if not request.user.is_authenticated: # 로그인하지 않은 유저의 경우 401 에러 리턴
      return Response(status=status.HTTP_401_UNAUTHORIZED)
    # serializer를 이용해서 room을 생성
    serializer = WriteRoomSerializer(data=request.data)
    # print(dir(serializer))
    if serializer.is_valid(): # False : 전송한 json 데이터 형식이 serializer에서 지정한 데이터 형식과 일치하지 않음!
      # serializer.create() # (주의) 절대 create, update method를 직접 호출하면 안됨!!! -> 대신 save method 호출!!!
      # [save()] : 새로운 room을 생성하는지 업데이트하는지 감지하여 create()나 update()를 대신 호출해줌
      # room을 만들 때는 owner(=user) 정보가 반드시 필요(not null)하므로 save method에 user에 관한 데이터를 보내주어야 함
      room = serializer.save(user=request.user) # create method에서 리턴된 instance를 가져와 'room'에 저장
      room_serializer = ReadRoomSerializer(room).data
      return Response(data=room_serializer, status=status.HTTP_200_OK) # ReadRoomSerializer를 사용해 생성된 room 객체 보여줌
    else:
      # print(serializer.errors)
      return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST) # respones로 에러메시지 보내기

  # rooms = Room.objects.all()
  # serialized_rooms = RoomSerializer(rooms, many=True) # 여러개의 room들에 대해서 serialize할 수 있도록
  # return Response(data=serialized_rooms.data)
'''

# custom pagination
class OwnPagination(PageNumberPagination):
  page_size = 20
  # 원하는 설정 추가 가능

# (2) 클래스형 뷰 사용 : APIView
class RoomsView(APIView):
  def get(self, request):
    # Manual Pagination(ViewSet을 이용하면 자동으로 해줌)
    paginator = OwnPagination()
    rooms = Room.objects.all()
    # reqeust를 paginator에게 parsing해줌 -> paginator가 page query argument를 찾아내야 함(?page=2)
    results = paginator.paginate_queryset(rooms, request)
    serializer = RoomSerializer(results, many=True)
    return paginator.get_paginated_response(serializer.data) # 단순 serializer 리턴 대신, paginator의 응답을 리턴해줌(count, previous, next 정보)

  def post(self, request): 
    if not request.user.is_authenticated: # 로그인하지 않은 유저의 경우 401 에러 리턴
      return Response(status=status.HTTP_401_UNAUTHORIZED)
    # serializer를 이용해서 room을 생성
    serializer = RoomSerializer(data=request.data)
    # print(dir(serializer))
    if serializer.is_valid(): # False : 전송한 json 데이터 형식이 serializer에서 지정한 데이터 형식과 일치하지 않음!
      # serializer.create() # (주의) 절대 create, update method를 직접 호출하면 안됨!!! -> 대신 save method 호출!!!
      # [save()] : 새로운 room을 생성하는지 업데이트하는지 감지하여 create()나 update()를 대신 호출해줌
      # room을 만들 때는 owner(=user) 정보가 반드시 필요(not null)하므로 save method에 user에 관한 데이터를 보내주어야 함
      room = serializer.save(user=request.user) # create method에서 리턴된 instance를 가져와 'room'에 저장
      room_serializer = RoomSerializer(room).data
      return Response(data=room_serializer, status=status.HTTP_200_OK) # ReadRoomSerializer를 사용해 생성된 room 객체 보여줌
    else:
      # print(serializer.errors)
      return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST) # respones로 에러메시지 보내기

'''
# (3) 제네릭 뷰 사용 : ListAPIView (많은 것을 커스터마이징할 필요 없을 때 간단하게 사용)
# [generic view] : page 등 여러가지 정보를 가진 뷰, 제네릭 뷰를 사용해야 간편한 pagination 기능 사용 가능.
class ListRoomsView(ListAPIView):
  # [queryset 필요]
  queryset = Room.objects.all()
  # [serializer_class 필요]
  serializer_class = RoomSerializer
'''

# ----------------------------------------------------------------------------------------------------- #

# 2. See Room
'''
class SeeRoomView(RetrieveAPIView):
  # [queryset 필요] -> queryset은 하나의 객체가 아닌 '리스트'를 의미함!
  queryset = Room.objects.all()
  # [serializer_class 필요]
  # serializer_class = BigRoomSerializer
  serializer_class = ReadRoomSerializer
  # [pk customizing]
  # lookup_url_kwarg = "pkkk"
'''

class RoomView(APIView):
  # pk로 Room Detail 정보를 가져오는 함수
  def get_room(self, pk):
    try:
      room = Room.objects.get(pk=pk)
      return room
    except Room.DoesNotExist:
      return None

  # Room Detail 보여주기
  def get(self, request, pk):
    # 여기서 직접 try-catch로 처리하는 대신 get_room() 함수에서 처리한 결과를 가져와서 사용
    room = self.get_room(pk)
    if room is not None:
      serializer = RoomSerializer(room).data
      return Response(serializer)
    else:
      return Response(status=status.HTTP_404_NOT_FOUND)
    '''
    try:
      room = Room.objects.get(pk=pk)
      serializer = ReadRoomSerializer(room).data
      return Response(serializer)
    except Room.DoesNotExist:
      return Response(status=status.HTTP_404_NOT_FOUND)
    '''

  def put(self, request, pk):
    room = self.get_room(pk)
    if room is not None:
      if room.user != request.user:
        return Response(status=status.HTTP_403_FORBIDDEN)
      # 찾은 room 정보를 instance로 하여 initailze(=update)**
      serializer = RoomSerializer(room, data=request.data, partial=True) # partial=True : 내가 바꾸고 싶은 데이터만 보내기 가능
      # print(serializer.is_valid(), serializer.errors) # False : partial=True로 부분 업데이트 가능하도록 변경!
      if serializer.is_valid():
        room = serializer.save() # serializer의 update method 호출
        return Response(RoomSerializer(room).data) # update된 room값 보여줌
      else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQEUST)
      return Response()
    else:
      return Response(status=status.HTTP_404_NOT_FOUND)

  def delete(self, request, pk):
    room = self.get_room(pk)
    if room is not None:
      if room.user != request.user:
        return Response(status=status.HTTP_403_FORBIDDEN)
      room.delete()
      return Response(status=status.HTTP_200_OK)
    else:
      return Response(status=status.HTTP_404_NOT_FOUND)

# Room Search
# TODO1 : 원하는 Room 찾기
# TODO2 : Pagenation
@api_view(["GET"])
def room_search(request):
  # manual paginator
  paginator = OwnPagination()
  # 모든 room이 아닌 조건에 맞는 room만 가져옴
  rooms = Room.objects.filter()
  results = paginator.paginate_queryset(rooms, request)
  serializer = RoomSerializer(results, many=True)
  return paginator.get_paginated_response(serializer.data) # 단순 serializer 리턴 대신, paginator의 응답을 리턴해줌(count, previous, next 정보)