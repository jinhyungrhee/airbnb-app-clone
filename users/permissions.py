from rest_framework.permissions import BasePermission

class IsSelf(BasePermission):

  # 각 object에 접근
  def has_object_permission(self, request, view, user):
    # serializer가 처리하고 있는 user가 reuqest user와 동일한지 체크
    return user == request.user