from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
import re


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(label='邮箱或用户名')
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data['identifier'].strip()
        password = data['password']

        # 判断是邮箱还是用户名
        EMAIL_RE = re.compile(r'^[^@]+@[^@]+\.[^@]+$')
        if EMAIL_RE.match(identifier):
            # 用邮箱查找用户
            try:
                user_obj = User.objects.get(email__iexact=identifier)
            except User.DoesNotExist:
                raise serializers.ValidationError('邮箱或密码错误')
            user = authenticate(username=user_obj.email, password=password)
        else:
            # 用用户名查找用户
            try:
                user_obj = User.objects.get(username__iexact=identifier)
            except User.DoesNotExist:
                raise serializers.ValidationError('用户名或密码错误')
            user = authenticate(username=user_obj.email, password=password)

        if not user:
            raise serializers.ValidationError('密码错误')
        if not user.is_active:
            raise serializers.ValidationError('账号已被禁用')
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'avatar', 'date_joined')
        read_only_fields = ('id', 'email', 'date_joined')
