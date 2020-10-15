from posts.models import Post, Comment
from posts.owner import OwnerDetailView, OwnerDeleteView
from django.views import View
from django.views.generic import DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from posts.forms import CreateForm, CommentForm
from django.http import HttpResponse
from django.contrib.humanize.templatetags.humanize import naturaltime
from posts.utils import dump_queries
from django.db.models import Q
from django.conf import settings


class HomeView(View):
    def get(self, request):
        return render(request, 'posts/index.html', {"settings": settings})


class PostListView(View):
    template_name = "posts/post_list.html"

    def get(self, request):
        strval = request.GET.get("search", False)
        if strval:
            query = Q(title__contains=strval)
            query.add(Q(text__contains=strval), Q.OR)
            objects = Post.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else:
            objects = Post.objects.all().order_by('-updated_at')[:10]
        # Augment the post_list
        for obj in objects:
            obj.natural_updated = naturaltime(obj.updated_at)

        ctx = {'post_list': objects, 'search': strval}
        retval = render(request, self.template_name, ctx)

        dump_queries()
        return retval;


class PostDetailView(OwnerDetailView):
    model = Post
    template_name = "posts/post_detail.html"

    def get(self, request, pk):
        x = Post.objects.get(id=pk)
        comments = Comment.objects.filter(post=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = {'post': x, 'comments': comments, 'comment_form': comment_form}
        return render(request, self.template_name, context)



class PostCreateView(LoginRequiredMixin, View):
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('posts:all')

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()
        return redirect(self.success_url)


class PostUpdateView(LoginRequiredMixin, View):
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('posts:all')

    def get(self, request, pk):
        pic = get_object_or_404(Post, id=pk, owner=self.request.user)
        form = CreateForm(instance=pic)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        pic = get_object_or_404(Post, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=pic)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        pic = form.save(commit=False)
        pic.save()

        return redirect(self.success_url)


class PostDeleteView(DeleteView):
    model = Post


def stream_file(request, pk):
    post = get_object_or_404(Post, id=pk)
    response = HttpResponse()
    response['Content-Type'] = post.content_type
    response['Content-Length'] = len(post.picture)
    response.write(post.picture)
    return response


# comment create and delete view
class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        f = get_object_or_404(Post, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, post=f)
        comment.save()
        return redirect(reverse('posts:post_detail', args=[pk]))


class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "posts/post_comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        post = self.object.post
        return reverse('posts:post_detail', args=[post.id])
