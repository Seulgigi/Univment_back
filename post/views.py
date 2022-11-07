from django.http import Http404, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from .models import Post, Category
from .serializers import PostSerializer, CategorySerializer
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
# Create your views here.

class PostCreate(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    lookup_field = 'id'
    serializer_class = PostSerializer

class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset1 = Category.objects.filter(isDefault = True)
        queryset2 = Category.objects.filter(generated_user = self.request.user)
        queryset = queryset1.union(queryset2)
        return queryset

class CategoryDetail(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    lookup_field = 'category'
    serializer_class = PostSerializer

    def get_queryset(self, *args, **kwargs):
        return (
            super().
            get_queryset(*args, **kwargs).filter(user=self.request.user.id).filter(category=self.kwargs['category'])
        ) 

    def destroy(self, request, *args, **kwargs):
        try:
            instance = Category.objects.all().get(id=self.kwargs['category'])
            self.perform_destroy(instance)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.request.method in ['DELETE']:
            category = Category.objects.all().get(id=self.kwargs['category'])

            if category.isDefault:
                self.permission_classes = [IsAdminUser,]

        return super(CategoryDetail, self).get_permissions()
                    
        
class TimeLine(generics.ListAPIView):
    queryset = Post.objects.filter(timeline=True).order_by('event_date')
    serializer_class = PostSerializer

    # 사용자가 작성한 글만 불러오게 하기
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs