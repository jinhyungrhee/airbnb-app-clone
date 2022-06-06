'''
from rest_framework import viewsets
from .models import Room
from .serializers import BigRoomSerializer

# ModelViewSet은 URL을 사용하지 않고도 List Room과 See Room을 만들어줌**
# ViewSet이 자동적으로 URL을 만들어줌** (CRUD 전부 제공)
class RoomViewset(viewsets.ModelViewSet):
  # queryset 필요
  queryset = Room.objects.all()
  # serializer_class 필요
  serializer_class = BigRoomSerializer
'''