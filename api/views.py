from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Team
from .serializers import TeamSerializer, UserSerializer


class TeamListCreate(generics.ListCreateAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Team.objects.filter(author=user)

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            print(serializer.errors)


class TeamDelete(generics.DestroyAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Team.objects.all()


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
