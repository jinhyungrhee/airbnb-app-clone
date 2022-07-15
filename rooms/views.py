# from rest_framework.decorators import api_view # (1)함수형 뷰 사용
from rest_framework.views import APIView # (2)클래스형 뷰 사용
# from rest_framework.generics import ListAPIView, RetrieveAPIView # (3)제네릭 뷰 사용
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from .models import Room
from .serializers import RoomSerializer
from .permissions import IsOwner

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

# custom pagination (ViewSets를 사용하면 따로 설정할 필요X)
# class OwnPagination(PageNumberPagination):
#   page_size = 20
#   # 원하는 설정 추가 가능

# (2) 클래스형 뷰 사용 : APIView
# RoomsView 삭제하고 ViewSets 사용하여 간단하게 구현*
'''
class RoomsView(APIView):
  def get(self, request):
    # Manual Pagination(ViewSet을 이용하면 자동으로 해줌)
    paginator = OwnPagination()
    rooms = Room.objects.all()
    # reqeust를 paginator에게 parsing해줌 -> paginator가 page query argument를 찾아내야 함(/?page=2)
    results = paginator.paginate_queryset(rooms, request)
    serializer = RoomSerializer(results, many=True, context={"request":request})
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

'''
# (3) 제네릭 뷰 사용 : ListAPIView (많은 것을 커스터마이징할 필요 없을 때 간단하게 사용)
# [generic view] : page 등 여러가지 정보를 가진 뷰, 제네릭 뷰를 사용해야 간편한 pagination 기능 사용 가능.
class ListRoomsView(ListAPIView):
  # [queryset 필요]
  queryset = Room.objects.all()
  # [serializer_class 필요]
  serializer_class = RoomSerializer
'''

# (4) ViewSets 사용 
class RoomViewSet(ModelViewSet):
  
  queryset = Room.objects.all()
  serializer_class = RoomSerializer

  # ViewSet의 권한 설정
  def get_permissions(self):
    
    # GET /rooms 또는 GET /rooms/1
    if self.action == "list" or self.action == "retrieve":
      permission_classes = [permissions.AllowAny] # 누구나 접근 가능
    elif self.action == "create":
      permission_classes = [permissions.IsAuthenticated] # 로그인된 유저만 가능
    # DELETE /rooms/1 또는 PUT /rooms/1
    else:
      permission_classes = [IsOwner]
    # permission_classes에 있는 모든 permission 메서드를 호출함
    return [permission() for permission in permission_classes]

  # action 데코레이터를 사용하면 함수명이 곧 url path가 됨!
  @action(detail=False)
  def search(self, request):
    # argument로 보내질 것들(/?max_price=30)
    max_price = request.GET.get('max_price', None) # 만약 url에 포함되어 있지 않으면, 그 argument는 None이라는 의미
    min_price = request.GET.get('min_price', None)
    beds = request.GET.get('beds', None)
    bedrooms = request.GET.get('bedrooms', None)
    bathrooms = request.GET.get('bathrooms', None)
    lat = request.GET.get('lat', None)
    lng = request.GET.get('lng', None)
    # 여러 조건들로 가득찬 dictionary 생성
    filter_kwargs = {}
    # __lte(less than or equal), __gte(greater than or equal), __startswith 연산 제공(DRF)
    if max_price is not None:
      filter_kwargs["price__lte"] = max_price
    if min_price is not None:
      filter_kwargs["price__gte"] = min_price
    if beds is not None:
      filter_kwargs["beds__gte"] = beds
    if bedrooms is not None:
      filter_kwargs["bedrooms__gte"] = bedrooms
    if bathrooms is not None:
      filter_kwargs["bathrooms__gte"] = bathrooms
    if lat is not None and lng is not None: # radius search
      filter_kwargs["lat__gte"] = float(lat) - 0.005
      filter_kwargs["lat__lte"] = float(lat) + 0.005
      filter_kwargs["lng__gte"] = float(lng) - 0.005
      filter_kwargs["lng__lte"] = float(lng) + 0.005
    paginator = self.paginator # ModelViewSet에서 제공하는 paginator
    # 모든 room이 아닌 조건에 맞는 room만 가져옴
    try:
      rooms = Room.objects.filter(**filter_kwargs) # argument들을 filter에 전달 (** -> double expansion 또는 unpacking)
    except ValueError:
      # query로 이상한 값을 보낼 경우, 모든 room을 리턴함 (에러 처리)
      rooms = Room.objects.all() 

    results = paginator.paginate_queryset(rooms, request)
    serializer = RoomSerializer(results, many=True)
    return paginator.get_paginated_response(serializer.data)



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
# RoomView 삭제하고 ViewSets로 간단하게 구현**
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
    # try:
    #   room = Room.objects.get(pk=pk)
    #   serializer = ReadRoomSerializer(room).data
    #   return Response(serializer)
    # except Room.DoesNotExist:
    #   return Response(status=status.HTTP_404_NOT_FOUND)
    

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
  '''

# Room Search
# TODO1 : 원하는 Room 찾기
# TODO2 : Pagenation
# @api_view(["GET"])
# def room_search(request):
#   # argument로 보내질 것들(/?max_price=30)
#   max_price = request.GET.get('max_price', None) # 만약 url에 포함되어 있지 않으면, 그 argument는 None이라는 의미
#   min_price = request.GET.get('min_price', None)
#   beds = request.GET.get('beds', None)
#   bedrooms = request.GET.get('bedrooms', None)
#   bathrooms = request.GET.get('bathrooms', None)
#   lat = request.GET.get('lat', None)
#   lng = request.GET.get('lng', None)
#   # 여러 조건들로 가득찬 dictionary 생성
#   filter_kwargs = {}
#   # __lte(less than or equal), __gte(greater than or equal), __startswith 연산 제공(DRF)
#   if max_price is not None:
#     filter_kwargs["price__lte"] = max_price
#   if min_price is not None:
#     filter_kwargs["price__gte"] = min_price
#   if beds is not None:
#     filter_kwargs["beds__gte"] = beds
#   if bedrooms is not None:
#     filter_kwargs["bedrooms__gte"] = bedrooms
#   if bathrooms is not None:
#     filter_kwargs["bathrooms__gte"] = bathrooms
#   if lat is not None and lng is not None: # radius search
#     filter_kwargs["lat__gte"] = float(lat) - 0.005
#     filter_kwargs["lat__lte"] = float(lat) + 0.005
#     filter_kwargs["lng__gte"] = float(lng) - 0.005
#     filter_kwargs["lng__lte"] = float(lng) + 0.005
#   #print(filter_kwargs) # {'price__lte': '30', 'beds__gte': '2', 'bathrooms__gte': '2'}
#   #print(*filter_kwargs) # price__lte beds__gte bathrooms__gte (unpacked)
#   # **filter_kwargs 는 모든 것을 price__lte='30', beds__gte='2', bathrooms__gte='2'이렇게 보이도록 바꿈 (unpacked X2)
#   # manual paginator
#   paginator = OwnPagination()
#   # 모든 room이 아닌 조건에 맞는 room만 가져옴
#   try:
#     rooms = Room.objects.filter(**filter_kwargs) # argument들을 filter에 전달 (** -> double expansion 또는 unpacking)
#   except ValueError:
#     # query로 이상한 값을 보낼 경우, 모든 room을 리턴함 (에러 처리)
#     rooms = Room.objects.all() 

#   results = paginator.paginate_queryset(rooms, request)
#   serializer = RoomSerializer(results, many=True)
#   return paginator.get_paginated_response(serializer.data) # 단순 serializer 리턴 대신, paginator의 응답을 리턴해줌(count, previous, next 정보)