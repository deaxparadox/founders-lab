from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated,])
async def check_authenticate_user(request):
    return Response({"messsage": "successfully"}, status=status.HTTP_200_OK)