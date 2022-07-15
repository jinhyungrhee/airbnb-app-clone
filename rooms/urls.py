from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views
# from . import viewsets

app_name = "rooms"

# (1) ViewSet 사용 (자동적으로 URL을 만들어줌, 매우 간단)
# 라우터 객체 사용
router = DefaultRouter()
router.register("", views.RoomViewSet)
# urlpatterns를 라우터 url로 대체함
urlpatterns = router.urls

# -------------------------------------------------------------------------------------------- #

# (2) view 사용 (함수형뷰, 클래스형뷰, 제네릭뷰)
# => ViewSet이 내부적으로 어떻게 동작하는지 알 수 있음!
'''
urlpatterns = [
  # path("", views.rooms_view), # 함수형 뷰 url
  path("", views.RoomsView.as_view()), # 클래스형 뷰(제네릭 뷰) url
  path("search/", views.room_search),
  path("<int:pk>/", views.RoomView.as_view()),
]
'''