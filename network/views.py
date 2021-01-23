from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import json
from django.core.paginator import Paginator

from .models import User, Post, PostForm

from .helpers import duration

def following(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    
    # query list of user that logged in user is following
    following = request.user.following.all()
    # get posts only from following list
    posts = Post.objects.filter(user__in=following).order_by('-edited_timestamp')

    return render(request, "network/index.html", {
        'posts': posts,
    })


def follow_unfollow(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Log In Required"}, status=400)

    if request.method == 'PUT' or request.method == 'POST':
        data = json.loads(request.body)

        logged_in_user = User.objects.get(username = data['logged_in_user'])
        user_profile = User.objects.get(username = data['user_profile'])
        

        # decide button text. if POST, then follow/unfollow from database
        if user_profile in logged_in_user.following.all():
            #print('logged in user IS following user profile')
            if request.method == 'POST':
                logged_in_user.following.remove(user_profile)
                followers = user_profile.followers.count()
                return JsonResponse({'message': 'Success. User profile unfollowed', 'followers': str(followers)}, status=200)

            return JsonResponse({'follow_unfollow_btn_text': 'Unfollow'}) # ran executed if request is PUT

        else:
            #print('logged in user NOT following user profile')
            if request.method == 'POST':
                logged_in_user.following.add(user_profile)
                followers = user_profile.followers.count()
                return JsonResponse({'message': 'Success. User profile followed', 'followers': str(followers)}, status=200)

            return JsonResponse({'follow_unfollow_btn_text': 'Follow'}) # ran executed if request is PUT
    else:
        return JsonResponse({"error": "PUT/POST Required"}, status=400)

def user_profile(request, username):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    # Get the user object with specified username
    try:
        user_obj = User.objects.get(username=username)
        followers = user_obj.followers.all()
        user_posts = Post.objects.filter(user = user_obj)
        #print(followers)
        #print(user_posts)
    except User.DoesNotExist:
        # if user does not exist, then show index
        return HttpResponseRedirect(reverse("index"))
    except:
        pass
    
    return render(request, "network/index.html", {
        'user_profile': user_obj,
        'followers': followers,
        'posts': user_posts,
    })

def index(request):
    # Post new post
    if request.method == 'POST' and request.user.is_authenticated:
        p = PostForm(request.POST)
        if p.is_valid():
            #print(p.cleaned_data['post_content'])
            r = Post(user = request.user, post_content = p.cleaned_data['post_content'])
            r.save()
            return HttpResponseRedirect(reverse("index"))

    # Query all posts
    posts = Post.objects.order_by('-edited_timestamp')
    #print(posts)

    # In case we want to display duration, not timestamp
    duration_dict = {}
    for post in posts:
        # print(post.id)
        # print(post.edited_timestamp)
        # print(duration(post.edited_timestamp))
        #print(post.likes)
        duration_dict[post.id] = duration(post.edited_timestamp)

    # generate post form
    form = PostForm()

    # paginate posts
    posts_paginated = Paginator(posts,5)

    # get requested page number from URL. User clicked prev/next button if not None
    pg = request.GET.get('pg') # returns None if no pg in URL

    # decide if we should display page 1 or not
    if pg == None:
        pg = 1
    else:
        pg = int(pg)

    # decide if there is a prev/next button
    pg_prev = None
    pg_next = None

    if posts_paginated.page(pg).has_previous():
        pg_prev = pg - 1
    
    if posts_paginated.page(pg).has_next():
        pg_next = pg + 1



    return render(request, "network/index.html", {
        'form': form,
        'posts': posts_paginated.page(pg),
        'durations': duration_dict,
        'pg_prev': pg_prev,
        'pg_next': pg_next,
    })


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
