from django.shortcuts import render, HttpResponse, redirect
# 导入数据模型ArticlePost
from article.models import ArticlePost
import markdown
# 引入ArticlePostForm表单类
from .forms import ArticlePostForm
# 引入User模型
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# 引入分页模块
from django.core.paginator import Paginator
# 引入 Q 对象 多参数查询
from django.db.models import Q
from comment.models import Comment

# 引入评论表单
from comment.forms import CommentForm


def article_list(request):
    # 根据GET请求中查询条件
    # 返回不同排序的对象数组
    search = request.GET.get('search')
    order = request.GET.get('order')
    # 用户搜索逻辑
    if search:
        if order == 'total_views':
            # 用 Q对象 进行联合搜索 Q(title__icontains=search)意思是在模型的title字段查询，icontains是不区分大小写的包含
            article_lists = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            ).order_by('-total_views')
        else:
            article_lists = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            )
    else:
        # 将 search 参数重置为空
        search = ''
        if order == 'total_views':
            article_lists = ArticlePost.objects.all().order_by('-total_views')  # 添加-为降序排序
        else:
            article_lists = ArticlePost.objects.all()
    paginator = Paginator(article_lists, 3)  # 每页显示 1 篇文章
    page = request.GET.get('page')  # 获取 url 中的页码
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)
    # 因为文章需要翻页把order也传递到模板,order给模板一个标识，提醒模板下一页应该如何排序
    context = { 'articles': articles, 'order': order, 'search': search }
    return render(request, 'article/list.html', context)


# 文章详情
def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    # 引入评论表单
    comment_form = CommentForm()
    # 取出文章评论
    comments = Comment.objects.filter(article=id).order_by('-created')
    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])  # update_fields=[]指定了数据库只更新total_views字段
    # 将markdown语法渲染成html样式# 将toc单独提取出来，我们先将Markdown类赋值给一个临时变量md
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',  # 包含 缩写、表格等常用扩展
            'markdown.extensions.codehilite',  # 语法高亮扩展
            'markdown.extensions.toc',  # 目录扩展
            ]
    )
    article.body = md.convert(article.body)
    context = { 'article': article, 'toc': md.toc, 'comments': comments, 'comment_form': comment_form}
    return render(request, 'article/detail.html', context)


# 写文章的视图
# 检查登录
@login_required(login_url='/userprofile/login/')
def article_create(request):
    if request.method == "POST":  # 判断用户是否提交数据
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)  # 保存数据，但暂时不提交到数据库中
            # 指定目前登录的用户为作者
            new_article.author = User.objects.get(id=request.user.id)

            new_article.save()  # 将新文章保存到数据库中
            # 保存 tags 的多对多关系
            article_post_form.save_m2m()
            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:  # 如果用户GET请求获取数据,则返回一个空的表单类对象，提供给用户填写。
        # 创建表单类实例
        article_post_form = ArticlePostForm()

        context = {'article_post_form': article_post_form,}
        return render(request, 'article/create.html', context)


# 安全删文章
# 提醒用户登录
@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        # 过滤非作者的用户
        if request.user != article.author:
            return HttpResponse("抱歉，你无权修改这篇文章。")
        article.delete()
        # 完成删除后返回文章列表
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")


# 更新文章
# 提醒用户登录
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.tags.set([*request.POST.get('tags').split(',')], clear=True)
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:article_detail", id=id)
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    else:  # 如果用户 GET 请求获取数据
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = {'article': article, 'article_post_form': article_post_form, 'tags': ','.join([x for x in article.tags.names()]),}
        return render(request, 'article/update.html', context)


def article_list(request):
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    # 初始化查询集
    article_lists = ArticlePost.objects.all()

    # 搜索查询集
    if search:
        article_lists = article_lists.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''

    # 标签查询集  filter(tags__name__in=[tag])，意思是在tags字段中过滤name为tag的数据条目
    if tag and tag != 'None':
        article_lists = article_lists.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        article_lists = article_lists.order_by('-total_views')

    paginator = Paginator(article_lists, 3)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    # 需要传递给模板（templates）的对象
    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'tag': tag,
    }

    return render(request, 'article/list.html', context)

