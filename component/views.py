import urllib

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django import template
from django.shortcuts import render_to_response,redirect
import logging
from django.template import RequestContext
from django.db import models
from django.conf import settings
from django.utils.importlib import import_module
from django.contrib.auth.models import User
from datetime import datetime

from urls import *
from component.models import Category,Component,Post,Comment,CategoryForm,ComponentForm,UserComponent,PostForm



# Create your views here.

class CategoryWithComponents:
    def __init__(self):
        self.name=''
        self.components=[]


def component_list(request):
    """This is to list all of the components grouped by categories."""

    if request.method == 'POST':
        form = ComponentForm(request.POST)
        if form.is_valid:
            component = form.save(commit=False)
            component.save()
            
            for maintainer in form.cleaned_data.get('maintainers'):
                usercomponent = UserComponent(user=maintainer,component=component)
                usercomponent.save()

        return redirect(reverse('component_list'))

    catos = Category.objects.all()

    categories_all = []
    my_categories = []

    flag = request.user.is_authenticated()
    if flag:
        maintainer = User.objects.get(username=request.user.username)
        
        components = maintainer.component_set.all().order_by('category')

        count = 0
        if components.exists():
            tmp = CategoryWithComponents()
            tmp.name = Category.objects.get(id=components[0].id)
            my_categories.append(tmp)
            
        for component in components:
            cato_name = Category.objects.get(id=component.id)
            if cato_name != my_categories[count].name:
                count = count + 1
                tmp = CategoryWithComponents()
                tmp.name = cato_name
                my_categories.append(tmp)

            
            my_categories[count].components.append(component)


    for cato in catos:
        tmp = CategoryWithComponents()
        tmp.name = cato.name

        components = Component.objects.filter(category = cato.id)
        tmp.components = components

        categories_all.append(tmp)

        
    return render_to_response('dashboard.html',{
        'categories':categories_all,
        'my_categories':my_categories,
        'is_login': flag,
        },
        context_instance=RequestContext(request)
    )
    

def component_add(request):
    # if the method is post, it is urled when the button "save and add another" is pressed
    # so save the item first
    if request.method=="POST":
	form = ComponentForm(request.POST)
	form.save()

    # (and) show a empty form to the user to add an item 
    new_form = ComponentForm(initial={
        'maintainers': request.user.username}
    )

    return render_to_response("add_items.html",{
	"title": "component",
	#"add_list": ["name","user","maintainer","repo_address"]
	"form" : new_form,
        },
        context_instance=RequestContext(request)
    )


def category_add(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
	form.save()
        if '_popup' in request.POST:
            return render_to_response("popup_response.html",{
                "name": request.POST.get('name'),
                }
        )

    new_form = CategoryForm()
    if '_popup' in request.GET:
        is_popup = True
    else:
        is_popup = False
    return render_to_response("add_items.html",{
	"title": "category",
	"form" : new_form,
        "is_popup": is_popup,
        },
        context_instance=RequestContext(request)
    )

def post_add(request):
    if request.method == "POST":
        form = PostForm(request.POST)
	form.save()
        if '_popup' in request.POST:
            return render_to_response("popup_response.html",
        )

    new_form = PostForm()
    if '_popup' in request.GET:
        is_popup = True
    else:
        is_popup = False
    return render_to_response("add_items.html",{
	"title": "post",
	"form" : new_form,
        "is_popup": is_popup,
        },
        context_instance=RequestContext(request)
    )

   

def component_detail(request,category_name,component_name):
    """ This is another style of showing the detail component,including its readme page. """
    
    component = Component.objects.get(name=component_name) 

    if request.POST.get('save',None):
        component_form = ComponentForm(request.POST,prefix='component',instance=component)
        post = Post.objects.get(title=component.post)
        post_form = PostForm(request.POST,prefix='post',instance=post)
        print component_form
        if component_form.is_valid:
            component_form = component_form.save(commit=False)
            component_form.save()

        if post_form.is_valid:
            post_form.save()

    if request.POST.get('comment',None):
        print "In comment"
        create_time = datetime.now()
        body = request.POST.get('text') 
        print body
        user = User.objects.get(username=request.user.username)

        comment = Comment(author=user,component=component,create_time=create_time,body=body)
        print comment
        comment.save()

    flag = request.user.is_authenticated()
    editable = False
    form = {}
    post = Post.objects.get(title=component.post)
    if flag:
        maintainers = component.maintainers.all()
        for maintainer in maintainers:
            if request.user.username == maintainer.username:
                editable = True
                
    component_form = ComponentForm(instance=component)
    post_form = PostForm(instance=post)

    comments = Comment.objects.filter(component=component.id)

    return render_to_response("component_detail.html",{
        'editable': editable,
        'componentform': component_form,
        'postform': post_form,
        'component_name': component_name,
        'post': component.post,
        'comments': comments,
        },
        context_instance=RequestContext(request)
    )


def component_edit(request,category_name,component_name):
#     
#     if request.method == "POST":
#         form = ComponentForm(request.POST)
#         if form.is_valid:
#             component = form.save(commit=False)
#             component.save()
# 
            

    component = Component.objects.get(name=component_name)
    print component
    print component.post
    post = Post.objects.get(title=component.post)


    component_form = ComponentForm(instance=component,prefix='component')
    post_form = PostForm(instance=post,prefix='post')


    return render_to_response("modify_item.html",{
        'component_form': component_form,
        'post_form': post_form,
        },
        context_instance=RequestContext(request)
    )   



