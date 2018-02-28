# django模型的使用

* [基本操作](#基本操作)
* [其他操作](#其他操作)
    * [创建数据库](#创建数据库)
    * [创建首页内容](#创建首页内容)
    * [标题列表](#标题列表)
    * [添加标题](#添加标题)
    * [标题详情](#标题详情)
    * [添加新条目](#添加新条目)
    * [更新条目](#更新条目)
* [用户创建](#用户创建)
    * [用户注册](#用户注册)
    * [用户登录](#用户登录)
    * [用户登出](#用户登出)
* [关联用户](#关联用户)
* [后台管理](#后台管理)


## 基本操作
1. 创建项目
```
django-admin.py startproject learning_log
```
2. 创建博客app
```
python manage.py startapp learning_logs
```
3. 创建用户app
```
python manage.py startapp users
```
4. 添加博客app和用户app到配置文件settings.py
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'learning_logs',
    'users',
]
```
5. 在其他app文件夹下创建urls.py，并且在根urls.py下进行引用
```
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'users/', include('users.urls', namespace='users')),
    url(r'', include('learning_logs.urls', namespace='learning_logs')),
]
```

## 其他操作

### 创建数据库
在learning_logs文件夹下的models.py中添加两个表
```
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Topic(models.Model):
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User)

    def __unicode__(self):
        return self.text


class Entry(models.Model):
    topic = models.ForeignKey(Topic)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.text[:50] + '...'

```
Topic表：标题表，字段包括名称，添加时间和所属用户  
Entry表：条目表，字段包括标题（一对一），内容，添加时间

命令行中执行：
```
python manage.py makemigrations
python manage.py migrate
```
同步数据库

### 创建首页内容
1. 在learning_logs文件夹下的urls.py中添加首页地址
```
    url(r'^$', views.index, name='index'),
```
2. 在learning_logs文件夹下的views.py中添加index方法
```
def index(request):
    return render(request, 'learning_logs/index.html')
```
3. 在learning_logs文件夹下创建templates文件夹（在templates文件夹下创建app名称的文件夹，此文件夹可以不创建），
然后再templates文件夹下创建index.html文件
```
{% extends "learning_logs/base.html" %}

{% block content %}
    <p>Learning Log helps you keep track of your learning, for any topic you`re learning about.</p>
{% endblock content %}
```
集成extends，其他内容在block 和endblock中添加
4. 由于所有页面都包含一个导航栏，所以公共管理base.html
```
<p>
    <a href="{% url 'learning_logs:index' %}">Learning Log</a>-
    <a href="{% url 'learning_logs:topics' %}">Topics</a>-
    {% if user.is_authenticated %}
        Hello, {{ user.username }}
        <a href="{% url 'users:logout' %}">logout</a>
    {% else %}
        <a href="{% url 'users:register' %}">register</a>
        <a href="{% url 'users:login' %}">login</a>
    {% endif %}
</p>

{% block content %}{% endblock content %}
```
代码中包含了几个链接，分别是首页，标题列表，注册，登录（退出），这些链接页面后面创建

### 标题列表
1. 在urls.py中添加地址
```
    url(r'^topics/$', views.topics, name='topics'),
```
2. 在views.py中添加topics方法
```
def topics(request):
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context=context)
```
3. 创建topics.html文件
```
{% extends "learning_logs/base.html" %}

{% block content %}
    <p>Topics</p>
    <ul>
        {% for topic in topics %}
            <li>
                <a href="{% url 'learning_logs:topic' topic.id %}">{{topic}}</a>
            </li>
        {% empty %}
            <li>No topics have been added yet.</li>
        {% endfor %}
    </ul>
<a href="{% url 'learning_logs:new_topic' %}">Add a new topic</a>
{% endblock content %}
```
其中包含添加和详情链接，这个后面创建
4. 添加其他链接地址  
在导航的列表跳转链接中将标题列表的链接添加

### 添加标题
1. 在urls.py中添加网址
```
    url(r'^new_topic/$', views.new_topic, name='new_topic'),
```
2. 在views.py中添加new_topic方法
```
def new_topic(request):
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return HttpResponseRedirect(reverse('learning_logs:topics'))
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context=context)
```
3. 创建forms.py文件，并且添加创建标题的表单
```
class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['text']
        labels = {'text': 'topic_text'}
```
4. 创建new_topic.html文件
```
{% extends "learning_logs/base.html" %}

{% block content %}
    <p>Add a new topic:</p>
    <form action="{% url 'learning_logs:new_topic' %}" method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button name="submit">add topic</button>
    </form>
{% endblock content %}
```
5. 添加创建标题的相关链接地址

### 标题详情
1. urls.py中添加地址
```
    url(r'^topics/(?P<topic_id>\d+)/$', views.topic, name='topic'),
```
2. views.py中添加topic方法
```
def topic(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by('date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context=context)
```
3. 创建topic.html文件
```
{% extends 'learning_logs/base.html' %}

{% block content %}
    <p>Topic: {{ topic }}</p>
    <p><a href="{% url 'learning_logs:new_entry' topic.id %}">Add a new entry</a></p>
    <p>Entries:</p>
    <ul>
        {% for entry in entries %}
            <li>
                <p>{{ entry.date_added|date:'M d, Y H:i' }}</p>
                <p>{{ entry.text|linebreaks }}</p>
                <p><a href="{% url 'learning_logs:edit_entry' entry.id %}">edit entry</a></p>
            </li>
        {% empty %}
            <li>
                There are no entries for this topic yet.
            </li>
        {% endfor %}
    </ul>
{% endblock content %}
```
4. 添加标题详情相关的链接

### 添加新条目
1. urls.py中添加创建新条目的地址
```
    url(r'^new_entry/(?P<topic_id>\d+)/$', views.new_entry, name='new_entry'),
```
2. views.py中添加new_entry方法
```
def new_entry(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    if request.method != 'POST':
        form = EntryForm
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic_id]))
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context=context)
```
3. 创建new_entry.html文件
```
{% extends "learning_logs/base.html" %}

{% block content %}
    <p>Topic:{{ topic }}</p>
    <p><a href="{% url 'learning_logs:topic' topic.id %}">{{ topic }}</a></p>
    <p>Add a new entry</p>
    <form action="{% url 'learning_logs:new_entry' topic.id %}" method="post">
        {% csrf_token%}
        {{ form.as_p }}
        <button name="submit">add entry</button>
    </form>
{% endblock content %}
```
4. 在forms.py中创建条目的表单
```
class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text']
        labels = {'text': 'entry_text'}
        widgets = {'text': forms.Textarea(attrs={'cols' : 80})}
```
5. 添加创建新条目的相关链接

### 更新条目
1. 在urls.py中添加地址
```
    url(r'^edit_entry/(?P<entry_id>\d+)/$', views.edit_entry, name='edit_entry'),
```
2. 在views.py中添加edit_entry方法
```
def edit_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404
    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic.id]))
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context=context)
```
3. 创建edit_entry.html文件
```
{% extends "learning_logs/base.html" %}

{% block content %}
    <p><a href="{% url 'learning_logs:topic' topic.id %}">{{ topic }}</a></p>
    <p>Entry entry:</p>
    <form action="{% url 'learning_logs:edit_entry' entry.id %}" method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button name="submit">edit entry</button>
    </form>
{% endblock content %}
```
4. 添加更新条目的相关链接

## 用户创建

### 用户注册
1. urls.py中添加地址
```
    url(r'^register/$', views.register, name='register'),
```
2. views.py中添加register方法
```
def register(request):
    if request.method != 'POST':
        form = UserCreationForm
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            authenticated_user = authenticate(username=new_user.username, password=request.POST['password1'])
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('learning_logs:index'))
    context = {'form': form}
    return render(request, 'users/register.html', context=context)
```
3. 创建register.html文件
```
{% extends 'learning_logs/base.html' %}

{% block content %}
<form action="{% url 'users:register' %}" method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button name="submit">register</button>
    <input type="hidden" name="next" value="{% url 'learning_logs:index' %}">
</form>
{% endblock content %}
```
4. 添加注册的相关地址

### 用户登录
1. urls.py中添加地址
```
    url(r'^login/$', login, {'template_name': 'users/login.html'}, name='login'),
```
2. 创建login.html文件
```
{% extends "learning_logs/base.html" %}

{% block content %}
    {% if form.errors %}
        <p>Your username and password didn`t match. Please try again</p>
    {% endif %}
    <form action="{% url 'users:login' %}" method="post">
        {% csrf_token %}
        {{form.as_p}}
        <button name="submit">login</button>
        <input type="hidden" name="next" value="{% url 'learning_logs:index' %}">
    </form>
{% endblock content %}
```
3. 添加登录的相关地址

### 用户登出
1. urls.py中添加地址
```
    url(r'^logout/$', views.logout_view, name='logout'),
```
2. views.py中添加logout_view方法
```
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('learning_logs:index'))
```
3. 添加登出的相关地址


## 关联用户
1. views.py中将需要先登录的方法前添加修饰
```
@login_required
```
2. settings.py中需要设置默认的登录地址
```
LOGIN_URL = '/users/login/'
```


## 后台管理
1. urls.py中默认登录地址，admin开头即可  
需要注意的是，此后台需要超级用户可以登录，之前的用户注册没有权限  
2. admin.py中添加实体类
```
admin.site.register(Topic)
admin.site.register(Entry)
```