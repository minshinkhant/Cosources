from django.urls import path, reverse_lazy
from . import views

app_name = 'posts'
urlpatterns = [
    path('', views.HomeView.as_view()),
    path('post', views.PostListView.as_view(), name='all'),
    path('post/<int:pk>', views.PostDetailView.as_view(), name='post_detail'),
    path('post/create',
         views.PostCreateView.as_view(success_url=reverse_lazy('posts:all')), name='post_create'),
    path('post/<int:pk>/update',
         views.PostUpdateView.as_view(success_url=reverse_lazy('posts:all')), name='post_update'),
    path('post/<int:pk>/delete',
         views.PostDeleteView.as_view(success_url=reverse_lazy('posts:all')), name='post_delete'),
    path('post_picture/<int:pk>', views.stream_file, name='post_picture'),
    path('post/<int:pk>/comment',
         views.CommentCreateView.as_view(), name='post_comment_create'),
    path('comment/<int:pk>/delete',
         views.CommentDeleteView.as_view(success_url=reverse_lazy('posts')), name='post_comment_delete'),
]
