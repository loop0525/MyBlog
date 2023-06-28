# 引入path
from django.urls import path

# 正在部署的应用的名称
from article import views

app_name = 'article'

urlpatterns = [
    # path函数将url映射到视图
    path('', views.article_list, name='article_list'),
    path('article-list/', views.article_list, name='article_list'),  # 参数name用于反查url地址，相当于给url起了个名字
    # 文章详情
    path('article-detail/<int:id>/', views.article_detail, name='article_detail'),
    # 写文章
    path('article-create/', views.article_create, name='article_create'),
    # 安全删除文章
    path(
        'article-safe-delete/<int:id>/',
        views.article_safe_delete,
        name='article_safe_delete'
    ),
    # 更新文章
    path('article-update/<int:id>/', views.article_update, name='article_update'),




]