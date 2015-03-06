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
from django.contrib.auth.models import User,Group
from datetime import datetime
from django.views.generic.edit import CreateView
from django.utils.html import escape, escapejs

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
        if form.is_valid():
            component = form.save(commit=False)
            component.save()
            
            for maintainer in form.cleaned_data.get('maintainers'):
                usercomponent = UserComponent(user=maintainer,component=component)
                usercomponent.save()

        return redirect(reverse('component_list'))

    catos = Category.objects.all()

    categories_all = []
    my_categories = []

    can_modify_category = False

    flag = request.user.is_authenticated()

    if flag:
        # get the login user information
        maintainer = User.objects.get(username=request.user.username)
        user_group = Group.objects.filter(user=maintainer.id)
        for group in user_group:
            print group.name
            if 'admin' == group.name:
                can_modify_category = True

        # get all the components
        components = maintainer.component_set.all().order_by('category')

        count = 0
        if components.exists():
            # initail the CategoryWithComponents struct
            tmp = CategoryWithComponents()
            tmp.name = Category.objects.get(id=components[0].category_id)
            my_categories.append(tmp)
            
        for component in components:
            # rearrange the components the login_user maintain
            cato_name = Category.objects.get(id=component.category_id)
            if cato_name != my_categories[count].name:
                count = count + 1
                tmp = CategoryWithComponents()
                tmp.name = cato_name
                my_categories.append(tmp)

            
            my_categories[count].components.append(component)

    # rearrange all the components
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
        'can_modify_category': can_modify_category,
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

class CategoryAddView(CreateView):
    """ This is the generic view used to get the object when add category window pop back. """

    model = Category
    fields = ['name']
    template_name = 'add_items.html'

    def get_context_data(self, **kwargs):
        context = super(CategoryAddView,self).get_context_data(**kwargs)
        if ('_popup' in self.request.GET):
            print "popup"
            context['is_popup'] = self.request.GET['_popup'] 
        return context

    def post(self, request, *args, **kwargs):
        ## Save the normal response
        self.object = None
        response = super(CategoryAddView,self).post(request, *args, **kwargs)
        ## This will fire the script to close the popup and update the list
        if "_popup" in request.POST:
            print "in post()"
            return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                (escape(self.object.pk), escapejs(self.object)))
        ## No popup, so return the normal response
        return response


# def category_add(request):
#     if request.method == "POST":
#         form = CategoryForm(request.POST)
# 	form.save()
#        
#         if '_popup' in request.POST:
#             print request.POST.get('name')
#             return render_to_response("popup_response.html",                {
#                 "name": request.POST.get('name'),
#                 }
#             )
# 
#     new_form = CategoryForm()
#     if '_popup' in request.GET:
#         is_popup = True
#     else:
#         is_popup = False
#     return render_to_response("add_items.html",{
# 	"title": "category",
# 	"form" : new_form,
#         "is_popup": is_popup,
#         },
#         context_instance=RequestContext(request)
#     )

class PostAddView(CreateView):
    model = Post
    fields = ['title','body']
    template_name = 'add_items.html'

    def get_context_data(self, **kwargs):
        context = super(PostAddView,self).get_context_data(**kwargs)
        if ('_popup' in self.request.GET):
            print "popup"
            context['is_popup'] = self.request.GET['_popup'] 
        return context

    def post(self, request, *args, **kwargs):
        ## Save the normal response
        self.object = None
        response = super(PostAddView,self).post(request, *args, **kwargs)
        ## This will fire the script to close the popup and update the list
        if "_popup" in request.POST:
            print "in post()"
            return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                (escape(self.object.pk), escapejs(self.object)))
        ## No popup, so return the normal response
        return response


# def post_add(request):
#     if request.method == "POST":
#         form = PostForm(request.POST)
# 	form.save()
#         if '_popup' in request.POST:
#             return render_to_response("popup_response.html",{
#                 'name': request.POST.get('title')
#                 }
#             )
# 
#     new_form = PostForm()
#     if '_popup' in request.GET:
#         is_popup = True
#     else:
#         is_popup = False
#     return render_to_response("add_items.html",{
# 	"title": "post",
# 	"form" : new_form,
#         "is_popup": is_popup,
#         },
#         context_instance=RequestContext(request)
#     )
# 
   

def component_detail(request,category_name,component_name):
    """ This is another style of showing the detail component,including its readme page. """
    
    component = Component.objects.get(name=component_name) 

    # save the modified component
    if request.POST.get('save',None):
        component_form = ComponentForm(request.POST,prefix='component',instance=component)
        post = Post.objects.get(title=component.post)
        post_form = PostForm(request.POST,prefix='post',instance=post)
        
        if post_form.is_valid():
            post_form.save()
            
        if component_form.is_valid():
            component_form = component_form.save(commit=False)
            component_form.save()

    # save the added comment
    if request.POST.get('comment',None):
        create_time = datetime.now()
        body = request.POST.get('text') 
        user = User.objects.get(username=request.user.username)

        comment = Comment(author=user,component=component,create_time=create_time,body=body)
        comment.save()

    
    flag = request.user.is_authenticated()
    editable = False
    form = {}
    post = Post.objects.get(title=component.post)

    # if the login_user is the maintainer of this component,there will be an edit in the detail page.
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
    """ This function is urled when the edit button is clicked."""        

    component = Component.objects.get(name=component_name)
    post = Post.objects.get(title=component.post)


    component_form = ComponentForm(instance=component,prefix='component')
    post_form = PostForm(instance=post,prefix='post')


    return render_to_response("modify_item.html",{
        'component_form': component_form,
        'post_form': post_form,
        'type': "component",
        'editable': True,
        },
        context_instance=RequestContext(request)
    )   


def component_delete(request,category_name,component_name):

    component = Component.objects.get(name=component_name)

    if request.POST.get('yes',None):
        # delete the post of the component
        post = Post.objects.get(title=component.post)
        post.delete()
        # delete all the comments of the component
        comments = Comment.objects.filter(component=component.id)
        comments.delete()
	component.delete()

        return redirect(reverse("component_list",args=[]))	
    
    return render_to_response("delete-confirm.html",{
	"title": "delete confirmation",
	"type": "component",
	"component": component.name,
	},
	context_instance=RequestContext(request)
    )

def category_delete(request,category_name):
    category = Category.objects.get(name=category_name)

    if request.POST.get('yes',None):
        category.delete()

        return redirect(reverse("component_list",args=[]))	
    
    return render_to_response("delete-confirm.html",{
	"title": "delete confirmation",
	"type": "category",
	"component": category.name,
	},
	context_instance=RequestContext(request)
    )
   

def category_edit(request,category_name):
    """This is urled when the category is clickedi or the modify is confirmed."""

    category = Category.objects.get(name=category_name)

    if request.POST.get("save",None):
        form = CategoryForm(request.POST,instance=category)
        form.save()
        return redirect(reverse("component_list",args=[]))	

    form = CategoryForm(instance=category)
    components = Component.objects.filter(category=category.id)
    editable = True
    if components.exists():
        editable = False

    return render_to_response("modify_item.html",{
        "type": "category",
        "category_form": form,
        "editable": editable,
        },
        context_instance=RequestContext(request)
    )

