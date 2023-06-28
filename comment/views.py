from django.shortcuts import HttpResponse, render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from article.models import ArticlePost
from .forms import CommentForm
from .models import Comment


# 文章评论
@login_required(login_url='/userprofile/login/')
def post_comment(request, article_id):
    article = get_object_or_404(ArticlePost, id=article_id)

    # 处理 POST 请求
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.user = request.user
            new_comment.save()
            return redirect(article)  # redirect()：返回到一个适当的url中当其参数是一个Model对象时，会自动调用这个Model对象的get_absolute_url()方法。
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 处理错误请求
    else:
        return HttpResponse("发表评论仅接受POST请求。")