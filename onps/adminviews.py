from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from newsapp.models import CustomUser,Category,Subcategory,News,Page,Comments
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
User = get_user_model()




def admin_only(view_func):
    """Require an authenticated primary administrator (user_type='1')."""
    from functools import wraps
    from django.shortcuts import redirect
    @login_required(login_url='/Login')
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if str(getattr(request.user, "user_type", "")) != "1":
            messages.error(request, "You do not have permission to access that page.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped

@admin_only
@login_required(login_url = '/Login')
def ADD_SUBADMIN(request):
   
    if request.method == "POST":
        pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not all([first_name, last_name, username, email, password]):
            messages.error(request, "Please complete all required fields.")
            return redirect('add_subadmin')
        if CustomUser.objects.filter(email__iexact=email).exists():
            messages.warning(request, 'Email already exists.')
            return redirect('add_subadmin')
        if CustomUser.objects.filter(username__iexact=username).exists():
            messages.warning(request, 'Username already exists.')
            return redirect('add_subadmin')
        try:
            validate_password(password)
        except ValidationError as exc:
            for error in exc.messages:
                messages.error(request, error)
            return redirect('add_subadmin')
        try:
            user = CustomUser(
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                username=username.strip(),
                email=email.strip(),
                user_type='2',
                profile_pic=pic,
            )
            user.set_password(password)
            user.save()
        except IntegrityError:
            messages.error(request, "That username or email is already in use.")
            return redirect('add_subadmin')
        messages.success(request, 'Subadministrator added successfully.')
        return redirect('add_subadmin')
    
    

    return render(request,'admin/add-subadmin.html')

@admin_only
@login_required(login_url='/Login')
def MANAGE_SUBADMIN(request):
    subadmin_list = CustomUser.objects.filter(user_type=2)
    paginator = Paginator(subadmin_list, 10)  # Show 10 subadmin per page

    page_number = request.GET.get('page')
    try:
        subadmin = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        subadmin = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        subadmin = paginator.page(paginator.num_pages)
    
    context = {'subadmin':subadmin,}
    return render(request,'admin/manage-subadmin.html',context)

@admin_only
@require_POST
@login_required(login_url='/Login')
def DELETE_SUBADMIN(request,id):
    subadmin = CustomUser.objects.get(id=id)
    subadmin.delete()
    messages.success(request,'Record Delete Succeesfully!!!')
    
    return redirect('manage_subadmin')

@admin_only
@login_required(login_url = '/Login')
def VIEW_SUBADMIN(request,id):
    user1 = CustomUser.objects.get(id = id,user_type=2)
    context = {
        "user1":user1,
    }
    return render(request,'admin/subadmin-profile.html',context)



@login_required(login_url='/Login')
def SUBADMIN_PROFILE_UPDATE(request):
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        userid = request.POST.get('userid')
        last_name = request.POST.get('last_name')
        

        try:
            customuser = get_object_or_404(CustomUser, id=userid, user_type=2)
            if str(getattr(request.user, "user_type", "")) != "1" and customuser.id != request.user.id:
                return HttpResponseForbidden("You cannot update another user's profile.")
            customuser.first_name = first_name
            customuser.last_name = last_name
            

            if profile_pic:
                customuser.profile_pic = profile_pic

            customuser.save()
            messages.success(request, "Your profile has been updated successfully")
            return redirect('view_subadmin', id=customuser.id)

        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, "Your profile update has failed")

    # In case of GET request or form errors, render the form with the current user's data
    if str(getattr(request.user, "user_type", "")) == "2":
        user1 = request.user
    else:
        return redirect('manage_subadmin')
    context = {"user1": user1}
    return render(request, 'admin/subadmin-profile.html', context)

@login_required(login_url='/Login')
def ADD_CATEGORY(request):
    if request.method == "POST":
        catname = request.POST.get('catname')
        catdes = request.POST.get('catdes')
        cat =Category(
            catname=catname,
            catdes=catdes,
        )
        cat.save()
        messages.success(request,'Category has been added succeesfully!!!')
        return redirect("add_category")
    
    return render(request,'admin/add_category.html')

@login_required(login_url='/Login')
def MANAGE_CATEGORY(request):
    
    cat_list = Category.objects.all()
    paginator = Paginator(cat_list, 10)  # Show 10 categories per page

    page_number = request.GET.get('page')
    try:
        categories = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        categories = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        categories = paginator.page(paginator.num_pages)

    context = {'categories': categories,
    }
    return render(request, 'admin/manage_category.html', context)
@require_POST
@login_required(login_url='/Login')
def DELETE_CATEGORY(request,id):
    cat = Category.objects.get(id=id)
    cat.delete()
    messages.success(request,'Record Delete Succeesfully!!!')
    
    return redirect('manage_category')

@login_required(login_url='/Login')
def UPDATE_CATEGORY(request,id):
    category = Category.objects.get(id=id)
    
    context = {
         'category':category,
        
    }

    return render(request,'admin/update_category.html',context)

@login_required(login_url='/Login')
def UPDATE_CATEGORY_DETAILS(request):
        if request.method == 'POST':
          cat_id = request.POST.get('cat_id')
          catname = request.POST.get('catname')
          catdes = request.POST.get('catdes')
          category = Category.objects.get(id=cat_id) 
          category.catname = catname
          category.catdes = catdes
          category.save()   
          messages.success(request,"Your category detail has been updated successfully")
          return redirect('manage_category')
        return render(request, 'admin/update_category.html')

@login_required(login_url = '/Login')
def ADD_SUBCATEGORY(request):    
    category = Category.objects.all()
    if request.method == "POST":
        cat_id = request.POST.get('cat_id')
        subcatname = request.POST.get('subcatname')
        cid = Category.objects.get(id=cat_id)
        Subcat = Subcategory(cat_id=cid, subcatname = subcatname,
        )
        Subcat.save()
        messages.success(request, 'Subcategory Added Succeesfully!!!')
        return redirect("add_subcategory")
    context = {
        'category':category,
        
    }
    return render(request,'admin/add_subcategory.html',context)


@login_required(login_url='/Login')
def MANAGE_SUBCATEGORY(request):
    subcategory_list = Subcategory.objects.all()
    paginator = Paginator(subcategory_list, 10)  # Show 10 subcategories per page

    page_number = request.GET.get('page')
    try:
        subcategories = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        subcategories = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        subcategories = paginator.page(paginator.num_pages)

    context = {'subcategories': subcategories,
     }
    return render(request, 'admin/manage_subcategory.html', context)

@require_POST
@login_required(login_url='/Login')
def DELETE_SUBCATEGORY(request,id):
    subcategory = Subcategory.objects.get(id=id)
    subcategory.delete()
    messages.success(request,'Record Delete Succeesfully!!!')
    
    return redirect('manage_subcategory')


@login_required(login_url='/Login')
def UPDATE_SUBCATEGORY(request,id):
    
    category = Category.objects.all()
    subcategory = Subcategory.objects.get(id=id)
    
    context = {
         'subcategory':subcategory,
         'category':category,
        
    }

    return render(request,'admin/update_subcategory.html',context)


@login_required(login_url='/Login')
def UPDATE_SUBCATEGORY_DETAILS(request):
        if request.method == 'POST':
          subcat_id = request.POST.get('subcat_id')
          cat_id = request.POST.get('cat_id')
          subcatname = request.POST.get('subcatname')
          subcategory = Subcategory.objects.get(id=subcat_id) 
          categoryid = Category.objects.get(id=cat_id) 
          subcategory.cat_id = categoryid
          subcategory.subcatname = subcatname
          subcategory.save()   
          messages.success(request,"Your subcategory detail has been updated successfully")
          return redirect('manage_subcategory')
        return render(request, 'admin/update_subcategory.html')



@login_required(login_url='/Login')

@login_required(login_url='/Login')
def get_subcat(request):
    if request.method == 'GET':
        c_id = request.GET.get('c_id')
        subcat = Subcategory.objects.filter(cat_id=c_id)
        subcat_options = ''
        for subcategory in subcat:
            subcat_options += f'<option value="{subcategory.id}">{subcategory.subcatname}</option>'
        return JsonResponse({'subcat_options': subcat_options})


@login_required(login_url='/Login')
def ADD_POST(request):
    category = Category.objects.all()
   
    if request.method == "POST":
        cat_id = request.POST.get('cat_id')
        subcategory_id_value = request.POST.get('subcategory_id')        
        posttitle = request.POST.get('posttitle')
        postdetails = request.POST.get('postdetails')
        status = request.POST.get('status')
        postimage = request.FILES.get('postimage')

        cid = Category.objects.get(id=cat_id)
        subcategory_id = Subcategory.objects.get(id=subcategory_id_value)
       

        # Accessing the UserReg instance associated with the logged-in user
        userregt = request.user.user_type

        postnews = News(
            cat_id=cid,
            subcategory_id=subcategory_id,
            posttitle=posttitle,
            postdetails=postdetails,
            status=status,
            postimage=postimage,
            postedby=userregt,
            updatedby=userregt
        )
        postnews.save()

        messages.success(request, 'News added Successfully!!!')
        return redirect("add_post")
    context = {
        'category': category,
       
    }    

    return render(request, 'admin/add_postnews.html', context)

@login_required(login_url='/Login')
def MANAGE_POSTS(request):
    posts_list = News.objects.all()
    paginator = Paginator(posts_list, 10)  # Show 10 subcategories per page

    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        posts = paginator.page(paginator.num_pages)

    context = {'posts': posts,
     }
    return render(request, 'admin/manage_postnews.html', context)


@require_POST
@login_required(login_url='/Login')
def DELETE_POSTS(request,id):
    postnews = News.objects.get(id=id)
    postnews.delete()
    messages.success(request,'Record Delete Succeesfully!!!')
    return redirect('manage_posts')


@login_required(login_url='/Login')
def VIEWS_POSTS(request,id):
    category = Category.objects.all()
    postnews = News.objects.get(id=id)
    
    context = {
         'postnews':postnews,
         'category':category
        
    }

    return render(request,'admin/update_news.html',context)


@login_required(login_url='/Login')
def UPDATE_POST(request):
    if request.method == 'POST':
        posts_id = request.POST.get('posts_id')
        subcat_id = request.POST.get('subcat_id')
        cat_id = request.POST.get('cat_id')
        posttitle = request.POST.get('posttitle')
        postdetails = request.POST.get('postdetails')
        status = request.POST.get('status')
        postimage = request.FILES.get('postimage')

        try:
            newspost = get_object_or_404(News, id=posts_id)
            subcategory = get_object_or_404(Subcategory, id=subcat_id)
            category = get_object_or_404(Category, id=cat_id)

            newspost.cat_id = category
            newspost.subcategory_id = subcategory
            newspost.posttitle = posttitle
            newspost.postdetails = postdetails
            newspost.status = status

            if postimage:
                newspost.postimage = postimage

            newspost.save()
            messages.success(request, "Your post detail has been updated successfully")
            return redirect('manage_posts')

        except (Subcategory.DoesNotExist, Category.DoesNotExist, News.DoesNotExist):
            messages.error(request, "Invalid ID provided for subcategory, category, or news post")
            return redirect('update_news')  # or any other appropriate redirection

    return render(request, 'admin/update_news.html')

@admin_only
@login_required(login_url='/Login')
def WEBSITE_UPDATE(request):
    if request.method == "POST":
        try:
            web_id = request.POST.get('web_id')
            page = Page.objects.get(id=web_id)
            page.pagetitle = request.POST.get('pagetitle')
            page.address = request.POST.get('address')
            page.aboutus = request.POST.get('aboutus')
            page.mobilenumber = request.POST.get('mobilenumber')
            page.email = request.POST.get('email')
            page.save()
            messages.success(request, "Page has been updated successfully")
            return redirect('website_update')
        except Page.DoesNotExist:
            messages.error(request, "Page does not exist")
            return redirect('website_update')
        except Exception as e:
            messages.error(request, "The website settings could not be saved. Please check the submitted values.")
            return redirect('website_update')
    
    pages = Page.objects.all()
    context = {
        "pages": pages,
    }
    return render(request, 'admin/website.html', context)

@login_required(login_url='/Login')
def ALLCOMMENTS(request):    
    all_comm = Comments.objects.all()
    paginator = Paginator(all_comm, 10)  # Show 10 enquiries per page

    page_number = request.GET.get('page')
    try:
        all_comm = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        all_comm = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        all_comm = paginator.page(paginator.num_pages)

    context = {
        'all_comm': all_comm,
    }
    return render(request, 'admin/all_comments.html', context)

@login_required(login_url='/Login')
def VIEW_COMMENTS(request,id):    
    view_comments = Comments.objects.filter(id=id)
      
    context = {
         'view_comments':view_comments,
         
    }
    return render(request,'admin/view-comments-details.html',context)

@login_required(login_url='/Login')
@require_POST
def UPDATE_COMMENTS_STATUS(request):
    comments_id = request.POST.get('comm_id')
    status_text = request.POST.get('status')

    if status_text not in {"Approved", "Unapproved"}:
        messages.error(request, "Invalid comment status.")
        return redirect('all_comments')

    comment = get_object_or_404(Comments, id=comments_id)
    comment.status = status_text
    comment.save(update_fields=["status", "updated_at"])
    messages.success(request, "Comment status updated successfully.")
    return redirect('all_comments')


@login_required(login_url='/Login')
def APPROVEDCOMMENTS(request):    
    approved_comm = Comments.objects.filter(status='Approved')
    paginator = Paginator(approved_comm, 10)  # Show 10 enquiries per page

    page_number = request.GET.get('page')
    try:
        approved_comm = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        approved_comm = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        approved_comm = paginator.page(paginator.num_pages)

    context = {
        'approved_comm': approved_comm,
    }
    return render(request, 'admin/comments_approved.html', context)

@login_required(login_url='/Login')
def UNAPPROVEDCOMMENTS(request):    
    unapproved_comm = Comments.objects.filter(status='Unapproved')
    paginator = Paginator(unapproved_comm, 10)  # Show 10 enquiries per page

    page_number = request.GET.get('page')
    try:
        unapproved_comm = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        unapproved_comm = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        unapproved_comm = paginator.page(paginator.num_pages)

    context = {
        'unapproved_comm': unapproved_comm,
    }
    return render(request, 'admin/comments_unapproved.html', context)


@require_POST
@login_required(login_url='/Login')
def DELETE_COMMENTS(request,id):
    del_com = Comments.objects.get(id=id)
    del_com.delete()
    messages.success(request,'Record Delete Succeesfully!!!')
    return redirect('all_comments')
