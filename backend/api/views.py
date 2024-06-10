from rest_framework import status
from .serializers import UserSerializer, ChatSerializer
from rest_framework.decorators import APIView
from rest_framework.response import Response
from .models import CustomUser, Chat
import jwt, datetime

fs = open('secret_key.txt', 'r')
secret_key = fs.read()

# Create your views here.
class UserLogin(APIView):
    def post(self, request):
        if 'username' not in request.data or 'password' not in request.data:
            return Response({'detail': 'You must fill in username and password.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.filter(username=request.data['username']).first()

        if not user:
            return  Response({'detail': 'An account is not exists!'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(request.data['password']):
            return Response({'detail':'Wrong Password.'}, status=status.HTTP_401_UNAUTHORIZED)

        check_online = (user.is_active == 1)
        
        if (check_online):
            return Response({'detail':'This account is being logged in elsewhere.'}, status=status.HTTP_401_UNAUTHORIZED)

        access_payload = {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
            'iat': datetime.datetime.utcnow()
        }

        access_token = jwt.encode(access_payload, secret_key, algorithm='HS256')

        refresh_payload = {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1440),
            'iat': datetime.datetime.utcnow()
        }

        rf_token = jwt.encode(refresh_payload, secret_key, algorithm='HS256')

        user.is_active = 1
        user.refresh_token = rf_token
        user.save()

        response = Response()
        response.set_cookie(key='access_token', value=access_token, httponly=True)
        response.set_cookie(key='refresh_token', value=rf_token, httponly=True)

        serializer = UserSerializer(instance=user)

        response.data = {
            'user': serializer.data,
        }

        return response

class UserRegister(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = CustomUser.objects.get(username=request.data['username'])
            user.set_password(request.data['password'])
            user.save()

            return Response({'user':serializer.data})

        for error in serializer.errors:
            if serializer.errors[error][0] == "This field may not be blank.":
                return Response({'detail': 'You must fill in all the infomation.'}, status=status.HTTP_400_BAD_REQUEST)
        if 'email' in serializer.errors:
            return Response({'detail' : serializer.errors['email'][0]}, status=status.HTTP_400_BAD_REQUEST)
        if 'username' in serializer.errors:
            return Response({'detail' : serializer.errors['username'][0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail' : str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

class UserLogout(APIView):
    def get(self, request):
        try:
            token = request.COOKIES.get('access_token')
            payload = jwt.decode(token, secret_key, algorithms=['HS256']) 
            
            try:
                response = Response()
                user = CustomUser.objects.filter(id=request.query_params['user_id']).first()
                user.is_active = 0
                user.refresh_token = ""
                user.save()

                response.delete_cookie('access_token')
                response.delete_cookie('refresh_token')

                response.data = {
                    'detail': 'success'
                }
                return response
        
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except jwt.ExpiredSignatureError:
            return Response({'detail':'Token has exprised!'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'detail':'Token is not valid!'}, status=status.HTTP_401_UNAUTHORIZED)


class UserView(APIView):
    def get(self, request):
        try:
            token = request.COOKIES.get('access_token')
            payload = jwt.decode(token, secret_key, algorithms=['HS256']) 
            
            # code

            return Response({'detail': 'success'}, status=status.HTTP_200_OK)
        
        except jwt.ExpiredSignatureError:
            return Response({'detail':'Token has exprised!'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'detail':'Token is not valid!'}, status=status.HTTP_401_UNAUTHORIZED)
