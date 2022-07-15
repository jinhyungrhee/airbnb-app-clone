import jwt
from django.conf import settings # (주의) 절대 settings.py 파일을 직접 import하면 안 됨! 이와 같은 방식으로 setting import
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, AllowAny
from rooms.serializers import RoomSerializer
from rooms.models import Room
from .models import User
from .serializers import UserSerializer
from .permissions import IsSelf

class UserViewSet(ModelViewSet):

  queryset = User.objects.all()
  serializer_class = UserSerializer # UserSerializer를 사용하기 때문에 DRF 테스트 화면에서 필드가 보이는 것!

  # GET /users 접근 제한
  def get_permissions(self):
    print(self.action)
    # permissions_classes = []
    if self.action == "list":  
      permissions_classes = [IsAdminUser] # 오직 admin user만 전체 리스트 확인 가능
    elif self.action == "create" or self.action == "retrieve" or self.action == "favs":
      permissions_classes = [AllowAny] # 누구나 create 가능
    else: # update, delete, toggle_favs
      permissions_classes = [IsSelf]

    return [permission() for permission in permissions_classes]

  @action(detail=False, methods=['POST']) # POST 메서드 지정 필요 (default=GET)
  def login(self, request):
    username = request.data.get("username")
    password = request.data.get("password")
    # 에러 처리
    if not username or not password:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    # django.contrib.auth의 authenticate 메서드 사용 -> username과 password를 넣고 맞으면 user 리턴
    user = authenticate(username=username, password=password)
    # user가 존재한다는 것을 authenticate()로 확인했으면 이 user를 JWT로 보내야 함!***
    # JWT(Json Web Token) : user에게 긴 String을 보내면 서버는 이 String을 decode함, 서버에서 decode를 하고나면 String안에 무언가가 나타남
    # 이 String은 userID일 수도 있고, e-mail일 수도 있고 뭐든 될 수 있음.
    
    # (1) Token 만들기 - PyJWT import(pipenv install pyjwt)
    # jwt를 encode : user에게 주고 싶은 내용(우리의 경우 id)을 담아서 암호화(encode), 그리고 secret과 algorithm을 입력함!
    # secret : 나만 아는 String값이어야 함(Django Secret key 사용) -> Token의 진위(authenticity)를 판단하기 위함. 로그인하기 위해서만 사용
    if user is not None:
      encoded_jwt = jwt.encode({"pk": user.pk}, settings.SECRET_KEY, algorithm="HS256") # settings.py에서 Key 가져와서 사용!
      # user가 /login으로 POST를 보낼 때 user는 /users/whoami 로 접근 가능
      return Response(data={'token':encoded_jwt, "id": user.pk}) # 여기서 나온 id(pk)로 /users/me 기능 대체 가능!
    else: # 잘못된 username이나 password를 보낼 경우
      return Response(status=status.HTTP_401_UNAUTHORIZED)

  @action(detail=True) # /users/<int:pk> 에서만 작동 (favs()의 argument로 pk 추가 필요!)
  def favs(self, request, pk): # 기존 FavsView의 get 기능
    # 외부인이 접근할 경우 anonymousUser가 되면서 에러 발생
    # user = request.user
    user = self.get_object() # 이 경우, View가 보여주는 object(pk)를 return하게 됨! -> get_object() 호출 시 바로 get_permission() 호출
    serializer = RoomSerializer(user.favs.all(), many=True).data
    return Response(serializer)

  # ** 같은 url에서 action을 만들어내는 방법 **
  # (데코레이터를 이용하여 favs를 선언하고 mapping을 이용하여 favs 확장함 - get/post/put/delete 모두 가능!)
  @favs.mapping.put
  def toggle_favs(self, request, pk):
    pk = request.data.get("pk", None)
    user = self.get_object()
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



# User 생성
# class UsersView(APIView):
#   def post(self, request):
#     serializer = UserSerializer(data=request.data) # (1)'data=' 꼭 써줘야함! (2)모든 정보를 원하므로 partial=True 생략
#     if serializer.is_valid():
#       new_user = serializer.save()
#       return Response(UserSerializer(new_user).data)
#     else:
#       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

# class MeView(APIView):
  
#   # permission_classes를 사용하면 'if request.user.is_authenticated:'사용하지 않아도 됨!
#   # 해당 class 전체에 모두 적용됨
#   # Function Based View에서는 @permission_classes([IsAuthenticated])의 데코레이터 추가하여 사용
#   permission_classes = [IsAuthenticated]


#   def get(self, request):
#     # if request.user.is_authenticated: # is_authenticated()로 하면 'bool' object is not callable 에러 발생!
#     return Response(UserSerializer(request.user).data)

#   # pk를 입력받으면 너가 해당 유저인지 체크하고 맞으면 profile update해줌
#   def put(self, request):
#     serializer = UserSerializer(request.user, data=request.data, partial=True) # request.user가 반드시 들어가야함!
#     # print(serializer.is_valid()) # True
#     if serializer.is_valid():
#       serializer.save()
#       return Response()
#     else:
#       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# fav를 추가하는 기능
class FavsView(APIView):

  permission_classes = [IsAuthenticated]

  # def get(self, request):
  #   user = request.user
  #   serializer = RoomSerializer(user.favs.all(), many=True).data
  #   return Response(serializer)


  # 해당 뷰에서는 어떠한 기록을 생성하지 않고 업데이트만 진행함
  # def put(self, request):
  #   pk = request.data.get("pk", None)
  #   user = request.user
  #   if pk is not None:
  #     # 해당 room 찾기
  #     try:
  #       room = Room.objects.get(pk=pk)
  #       # 만약 찾은 room이 user의 favs 리스트 안에 존재한다면 delete
  #       if room in user.favs.all():
  #         user.favs.remove(room)
  #       # 만약 찾은 room이 user의 favs 리스트 안에 없다면 추가
  #       else:
  #         user.favs.add(room)
  #       return Response()
  #     except Room.DoesNotExist:
  #       pass
  #   return Response(status=status.HTTP_400_BAD_REQUEST)

# 나의 위치를 파악하기 위해서 call할 수 있는 URL이 필요함(로그인하면 id를 알 수 없음) -> 함수를 분리한 이유
# 작은 기능은 함수형 뷰(api_view) 사용
# @api_view(["GET"])
# def user_detail(request, pk):
#   try:
#     user = User.objects.get(pk=pk)
#     return Response(ReadUserSerializer(user).data)
#   except User.DoesNotExist:
#     return Response(status=status.HTTP_404_NOT_FOUND)

# Login View -> 별 기능이 없기 때문에 Function Based View 사용
# @api_view(["POST"])
# def login(request):
#   username = request.data.get("username")
#   password = request.data.get("password")
#   # 에러 처리
#   if not username or not password:
#     return Response(status=status.HTTP_400_BAD_REQUEST)
#   # django.contrib.auth의 authenticate 메서드 사용 -> username과 password를 넣고 맞으면 user 리턴
#   user = authenticate(username=username, password=password)
#   # user가 존재한다는 것을 authenticate()로 확인했으면 이 user를 JWT로 보내야 함!***
#   # JWT(Json Web Token) : user에게 긴 String을 보내면 서버는 이 String을 decode함, 서버에서 decode를 하고나면 String안에 무언가가 나타남
#   # 이 String은 userID일 수도 있고, e-mail일 수도 있고 뭐든 될 수 있음.
  
#   # (1) Token 만들기 - PyJWT import(pipenv install pyjwt)
#   # jwt를 encode : user에게 주고 싶은 내용(우리의 경우 id)을 담아서 암호화(encode), 그리고 secret과 algorithm을 입력함!
#   # secret : 나만 아는 String값이어야 함(Django Secret key 사용) -> Token의 진위(authenticity)를 판단하기 위함. 로그인하기 위해서만 사용
#   if user is not None:
#     encoded_jwt = jwt.encode({"pk": user.pk}, settings.SECRET_KEY, algorithm="HS256") # settings.py에서 Key 가져와서 사용!
#     return Response(data={'token':encoded_jwt})
#   else: # 잘못된 username이나 password를 보낼 경우
#     return Response(status=status.HTTP_401_UNAUTHORIZED)
  
#   # (**주의**) 민감한 정보는 JWT 토큰에 담아선 안 된다!(ex 비밀번호, 이메일주소, username 등)
#   # -> 단순히 user를 구별할 수 있는 최소한의 식별자 수준의 정보만 넣어야 함! (ex id(user.pk) 정도만 가능) 
#   # -> 누구나 jwt.io 사이트에 가서 나의 jwt 토큰을 해독할 수 있기 때문!!!
#   # JWT 사용 이유 : 
#   # 누구나 JWT를 해독할 수 있지만, 서버는 이 token을 받아서 token에 대한 어떠한 변경사항(modified)이 하나라도 있었는지 판단함!
#   # 따라서 token 안에 어떤 정보가 있는지 누가 보든 말든 신경을 안써도 됨!
#   # 우리가 신경쓰는 부분은 그 누구도 우리 token을 건들지 않았다는 것을 확인하는 것임

#   # (2) Token 해독하기
#   # user가 우리에게 token을 보냈을 때, 우리는 그것을 받아서 해독하고 그 정보로 user를 찾아서 request.user를 알아냄

