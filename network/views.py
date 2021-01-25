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

from .helpers import duration, paginate_post

def like_unlike(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Log In Required"}, status=403)
    
    if request.method != 'PUT':
        return JsonResponse({"error": "PUT Required"}, status=405)

    data = json.loads(request.body)

    try:
        post_obj = Post.objects.get(pk = data['postid'])
    except:
        return JsonResponse({"error": "Cannot get post from DB"}, status=500)

    try:
        if request.user in post_obj.likes.all():
            # remove user from likes list
            post_obj.likes.remove(request.user)
        else:
            # add user to likes list
            post_obj.likes.add(request.user)
    except:
        return JsonResponse({"error": "Cannot update likes from post object"}, status=500)

    return JsonResponse({"message": "Sucess liking/unliking post", "likes_count": post_obj.likes.count()}, status=200)

def edit_save(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Log In Required"}, status=403)
    
    if request.method != 'PUT':
        return JsonResponse({"error": "PUT Required"}, status=405)
    
    data = json.loads(request.body)

    post_obj = Post.objects.get(pk = data['postid'])

    if request.user != post_obj.user:
        return JsonResponse({"error": "Non owner of post trying to edit"}, status=403)

    post_obj.post_content = data['new_content']
    post_obj.save()

    return JsonResponse({'message': 'Success.'}, status=200)


def following(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    
    # query list of user that logged in user is following
    following = request.user.following.all()
    # get posts only from following list
    posts = Post.objects.filter(user__in=following).order_by('-created_timestamp')

    # paginate post
    p = paginate_post(posts, request.GET.get('pg'))

    return render(request, "network/index.html", {
        'posts': p['posts_paginated'].page(p['pg']),
        'p': p,
    })


def follow_unfollow(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Log In Required"}, status=403)

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

            return JsonResponse({'follow_unfollow_btn_text': 'Unfollow'}, status = 200) # ran executed if request is PUT

        else:
            #print('logged in user NOT following user profile')
            if request.method == 'POST':
                logged_in_user.following.add(user_profile)
                followers = user_profile.followers.count()
                return JsonResponse({'message': 'Success. User profile followed', 'followers': str(followers)}, status=200)

            return JsonResponse({'follow_unfollow_btn_text': 'Follow'}, status = 200) # ran executed if request is PUT
    else:
        return JsonResponse({"error": "PUT/POST Required"}, status=405)

def user_profile(request, username):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    # Get the user object with specified username
    try:
        user_obj = User.objects.get(username=username)
        followers = user_obj.followers.all()
        posts = Post.objects.filter(user = user_obj).order_by('-created_timestamp')
        #print(followers)
        #print(user_posts)
    except User.DoesNotExist:
        # if user does not exist, then show index
        return HttpResponseRedirect(reverse("index"))
    except:
        pass

    # paginate post
    p = paginate_post(posts, request.GET.get('pg'))
    
    return render(request, "network/index.html", {
        'user_profile': user_obj,
        'followers': followers,
        'posts': p['posts_paginated'].page(p['pg']),
        'p': p,
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
    posts = Post.objects.order_by('-created_timestamp')
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

    # paginate post
    p = paginate_post(posts, request.GET.get('pg'))

    return render(request, "network/index.html", {
        'form': form,
        'posts': p['posts_paginated'].page(p['pg']),
        'durations': duration_dict,
        'p': p,
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
