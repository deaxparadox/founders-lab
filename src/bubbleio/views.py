from traceback import format_exc
from uuid import uuid4

from asgiref.sync import sync_to_async
from adrf.views import APIView
from django.db import IntegrityError
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from bubbleio.models import BubbleUserModel
from bubbleio.serializers import BubbleDataSerializer, BubbleRefreshTokenSerializer
from utils import base64
from utils.exceptions import SIDTimeOutException


class BubbleDataView(APIView):
    async def get(self, request):
        try:
            sid_key = request.query_params.get('sid')
            if not sid_key:
                return Response({"error": "Invalid session id"}, status=status.HTTP_400_BAD_REQUEST)
            
            sid_value = cache.get(sid_key)
            
            if not sid_value:
                return Response({"error": "Autentication session expired, please login in bubble dashboard again."}, status=status.HTTP_400_BAD_REQUEST)
            
            data = await base64.decode_string(sid_value)
            await base64.check_encoded_str_validity(data.get("expire_at"))
            bubble_user = await BubbleUserModel.objects.aget(
                Q(bubble_user_id=data.get("bubble_user_id")) & 
                Q(bubble_user_email=data.get("bubble_user_email"))
            )
            
            refresh_token = await sync_to_async(RefreshToken.for_user)(bubble_user)
            access_token = refresh_token.access_token
            
            tokens = {
                "refresh": str(refresh_token),
                "access": str(access_token)
            }
            
            return Response({"messsage": tokens}, status=status.HTTP_200_OK)
        
        except BubbleUserModel.DoesNotExist as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except BubbleUserModel.MultipleObjectsReturned as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except SIDTimeOutException as e:
            return Response({"error": "Autentication session expired, please login in bubble dashboard again."}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    async def post(self, request):
        try:
            serializer_data = {
                "user_id": request.query_params.get("user_id"),
                "email": request.query_params.get("email")    
            }
            serializer = BubbleDataSerializer(data=serializer_data)
            if not serializer.is_valid():
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            payload = {
                "bubble_user_id": serializer.validated_data.get("user_id"),
                "bubble_user_email": serializer.validated_data.get("email"),
            }
            
            
            bubble_user, created = await BubbleUserModel.objects.aget_or_create(
                bubble_user_id=payload.get("bubble_user_id"),
                bubble_user_email=payload.get("bubble_user_email"),
            )   
            if created:
                bubble_user.set_password(settings.BUBBLE_PASSWORD_DEFAULT)
                await bubble_user.asave()
            
            sid_key = str(uuid4())
            sid_value = await base64.encode_string(payload)
            cache.set(sid_key, sid_value, timeout=settings.CACHE_TTL)
            
            return Response(
                {
                    "redirect_url": settings.FRONTEND_URL.format(sid_key),
                },
                status=status.HTTP_200_OK
            )
        
        except IntegrityError:
            # If creation fails due to race condition, get the existing user
            bubble_user = await BubbleUserModel.objects.aget(
                bubble_user_id=payload.get("bubble_user_id")
            )
        
            sid_key = str(uuid4())
            sid_value = await base64.encode_string(payload)
            cache.set(sid_key, sid_value, timeout=settings.CACHE_TTL)
            
            return Response(
                {
                    "redirect_url": settings.FRONTEND_URL.format(sid_key),
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            print(format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class BubbleRefreshTokenView(APIView):
    async def post(self, request):
        try:
            serializer = BubbleRefreshTokenSerializer(data=request.data)
            if serializer.is_valid():
                refresh = RefreshToken(serializer.validated_data.get('refresh'))
                new_access_token = str(refresh.access_token)
                return Response({"message": {"access": new_access_token}}, status=status.HTTP_201_CREATED)
            return Response(
                {
                    "error": serializer.errors,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)