from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


try:
    from ..response import ApiResponse,ApiState
except:
    from ...rest.response import ApiResponse, ApiState


class UserAuthView(viewsets.ViewSetMixin,ObtainAuthToken):
    authModel = None
    @action(methods=['post'], detail=False)
    def register(self, request):

        if self.authModel is None:
            return ApiResponse(ApiState.exception, "login error: TokenAuthView can not be None (authModel inherit from User model class )", "")
        model = self.authModel
        try:
            #该处代码参照ObtainAuthToken
            serializer = self.serializer_class(data=request.data,
                                               context={'request': request})
            serializer.is_valid(raise_exception=False)
            data = serializer.data

            us = model.objects.filter(username=data['username'])
            if us.count() > 0:
                return ApiResponse(ApiState.failed, "用户名已存在", {})

            newObj = model.objects.create(username=data['username'])
            newObj.set_password(serializer.data['password'])
            newObj.save()
            token, created = Token.objects.get_or_create(user=newObj)

            return ApiResponse(ApiState.success, "注册成功", {'token': token.key})
        except Exception as e:
            raise APIException(e)


    @action(methods=['post'], detail=False)
    def login(self, request, *args, **kwargs):
        # 该处代码参照ObtainAuthToken
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)

        if self.authModel is None:
            return ApiResponse(ApiState.exception, "login error: TokenAuthView can not be None (authModel inherit from User model class )", "")
        baseUser = serializer.validated_data['user']
        user = eval(('baseUser.%s' % (self.authModel.__name__.lower())))
        # user = serializer.validated_data['user'].member
        token, created = Token.objects.get_or_create(user=user)
        return ApiResponse(ApiState.success, "登录成功", {'token': token.key})


