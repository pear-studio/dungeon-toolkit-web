from rest_framework import serializers
from .models import Bot
import secrets


class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = [
            'id', 'bot_id', 'nickname', 'master', 'master_qq', 'version',
            'description', 'is_public', 'status', 'last_seen',
            'created_at', 'updated_at', 'api_key'
        ]
        read_only_fields = ['id', 'api_key', 'master', 'status', 'last_seen', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['api_key'] = secrets.token_hex(32)
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if instance.master == request.user:
                data['api_key'] = instance.api_key
            else:
                data.pop('api_key', None)
        else:
            data.pop('api_key', None)
        return data


class BotRegistrationSerializer(serializers.Serializer):
    bot_id = serializers.CharField(max_length=20)
    nickname = serializers.CharField(max_length=100)
    master_id = serializers.CharField(max_length=20)
    version = serializers.CharField(max_length=50, required=False, allow_blank=True, default='')
    description = serializers.CharField(required=False, allow_blank=True, default='')


class BotHeartbeatSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['online', 'offline'], required=False, default='online')
