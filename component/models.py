#-*-coding:utf-8-*-

from django.db import models
from django import forms
from django.forms import ModelForm,widgets
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User



# Create your models here.
# 
# class User(models.Model):
#     """This is the definition of database user"""
# 
#     name = models.CharField(max_length=64)
#     create_time = models.DateTimeField('create date')
#     expire_time = models.DateTimeField('expire date')
#     passwd = models.CharField(max_length=64)
#     last_login = models.DateTimeField('last_login')
# 
#     def __unicode__(self):
#         return self.name
# 
#     class Meta:
#         db_table = 'user'


class RelatedFieldWidgetCanAdd(widgets.Select):

    def __init__(self, related_model, related_url=None, *args, **kw):

        super(RelatedFieldWidgetCanAdd, self).__init__(*args, **kw)

        if not related_url:
            rel_to = related_model
            info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
            related_url = 'admin:%s_%s_add' % info

        # Be careful that here "reverse" is not allowed
        self.related_url = related_url

    def render(self, name, value, *args, **kwargs):
        self.related_url = reverse(self.related_url)
        output = [super(RelatedFieldWidgetCanAdd, self).render(name, value, *args, **kwargs)]
        output.append(u'<a href="%s" class="add-another" id="add_id_%s" onclick="return showAddAnotherPopup(this);"> ' % \
            (self.related_url, name))
        output.append(u'<img src="%sadmin/img/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.STATIC_URL, 'Add Another'))                                                                                                                               
        return mark_safe(u''.join(output))


class Category(models.Model):
    """This is the definition of database category"""

    name = models.CharField(max_length=64)

    def __unicode__(self):
	return self.name

    class Meta:
        db_table = 'category'


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = 'post'


class Component(models.Model):
    """This is the definition of database component"""

    name = models.CharField(max_length=64)
    category = models.ForeignKey(Category,verbose_name="the related category")
    post = models.ForeignKey(Post)
    user = models.CharField(max_length=64)
    maintainers =  models.ManyToManyField(User, through='UserComponent')
    repo_address =  models.CharField(max_length=200,blank=True)

    def __unicode__(self):
	return self.name

    class Meta:
        db_table = 'component'


class UserComponent(models.Model):
    """This is the relationship of user and component"""

    user = models.ForeignKey(User)  
    component = models.ForeignKey(Component)  
      
    class Meta:  
        db_table = "maintain" 

# 
# class Group(models.Model):
#     """This is the definition of database group"""
# 
#     name = models.CharField(max_length=64)
# 
#     def __unicode__(self):
#         return self.name
# 
#     class Meta:
#         db_table = 'group'


class CategoryForm(ModelForm):
    class Meta:
        model = Category


class PostForm(ModelForm):
    class Meta:
        model = Post

class ComponentForm(ModelForm):
    
    category = forms.ModelChoiceField(
        required = True,
        queryset = Category.objects.all(),
        widget = RelatedFieldWidgetCanAdd(
            Category, 
            related_url="category_add_in_component")
    )

    post = forms.ModelChoiceField(
        required = False,
        queryset = Post.objects.all(),
        widget = RelatedFieldWidgetCanAdd(
            Post,
            related_url = 'post_add_in_component'
        )
    )

    maintainers = forms.ModelMultipleChoiceField(
        initial = '',
        queryset = User.objects.all(),
        
    )

    class Meta:
        model = Component

class ComponentPostForm(ComponentForm,PostForm):    pass
