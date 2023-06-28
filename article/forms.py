# 引入表单类
from django import forms
from .models import ArticlePost


# 写文章的表单类
class ArticlePostForm(forms.ModelForm):
    class Meta:
        # 指明数据模型来源
        model = ArticlePost
        # 定义表单包含的字段,就把models.py中的ArticlePost表中的字段关联到了ModelForm这里
        fields = ('title', 'body', 'tags')