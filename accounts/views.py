from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer, LoginSerializer, TeacherSerializer, UserSerializer
from .models import Teacher


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TeacherListView(generics.ListAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    def get_queryset(self):
        """
        Optionally filters the teachers by 'fullname' and 'speciality' parameters.
        """
        queryset = self.queryset
        fullname = self.request.query_params.get('fullname')
        speciality = self.request.query_params.get('speciality')
        if fullname:
            queryset = queryset.filter(fullname__icontains=fullname)
        if speciality:
            queryset = queryset.filter(speciality__icontains=speciality)
        return queryset


class UserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieves the current authenticated user.
        """
        return self.request.user
