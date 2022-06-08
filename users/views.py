from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from .models import User
from .serializers import ReadUserSerializer

class MeView(APIView):

  def get(self, request):
    if request.user.is_authenticated: # is_authenticated()로 하면 'bool' object is not callable 에러 발생!
      return Response(ReadUserSerializer(request.user).data)

  # pk를 입력받으면 너가 해당 유저인지 체크하고 맞으면 profile update해줌
  def put(self, request):
    pass

# 나의 위치를 파악하기 위해서 call할 수 있는 URL이 필요함(로그인하면 id를 알 수 없음) -> 함수를 분리한 이유
# 작은 기능은 함수형 뷰(api_view) 사용
@api_view(["GET"])
def user_detail(request, pk):
  try:
    user = User.objects.get(pk=pk)
    return Response(ReadUserSerializer(user).data)
  except User.DoesNotExist:
    return Response(status=status.HTTP_404_NOT_FOUND)

