from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core import serializers
from django.urls import reverse
from forum.models import Question, Reply
from product_catalog.models import Car
from pytz import timezone
import json

# Create your views here.
def show_forum(request) :
    cars = Car.objects.all()
    
    context = {
        'cars' : cars
    }
    
    return render(request, 'show_forum.html', context)

@csrf_exempt
def get_questions_json(request):
    sort_by = request.GET.get('sort', 'terbaru')
    category = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    questions = Question.objects.all().order_by('-created_at')
    
    if search_query:
        questions = questions.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )
        
    if category:
        questions = questions.filter(category=category)
        
    if sort_by == 'terbaru':
        pass
    elif sort_by == 'populer':
        questions = questions.annotate(reply_count=Count('reply')).order_by('-reply_count', '-created_at')
        
    paginator = Paginator(questions, 10)
    page = request.GET.get('page', 1)
    questions_page = paginator.get_page(page)
    
    wib = timezone('Asia/Jakarta')

    questions_data = json.loads(serializers.serialize('json', questions_page))
    for item in questions_data:
        question = Question.objects.get(pk=item['pk'])
        item['fields']['username'] = question.user.username
        item['fields']['reply_count'] = question.reply_set.count()
        
        wib_time = question.created_at.astimezone(wib)
        item['fields']['created_at'] = wib_time.strftime("%d %b %Y, %H:%M WIB")

    return JsonResponse({
        'questions': questions_data,
        'total_pages': paginator.num_pages,
        'current_page': int(page)
    })
    
@csrf_exempt
@require_POST
@login_required(login_url='/auth/login')
def create_question(request):
    try:
        user = request.user
        car_id = request.POST.get('car_id')
        title = strip_tags(request.POST.get('title'))
        content = strip_tags(request.POST.get('content'))
        category = request.POST.get('category')
        
        print(f"Received data: title={title}, content={content}, category={category}, car_id={car_id}")  # Debug print
        
        if not title.strip() or not content.strip():
            return JsonResponse({
                'status': 'error',
                'message': 'Title and content are required'
            }, status=400)
        
        car = None
        if car_id and car_id.strip():
            try:
                car = get_object_or_404(Car, pk=car_id)
            except (ValueError, Http404):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid car ID'
                }, status=400)
        
        new_question = Question(
            user=user,
            car=car,
            title=title,
            category=category,
            content=content
        )
        
        new_question.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Question created successfully'
        }, status=201)
    except Exception as e:
        print(f"Error creating question: {str(e)}")  # Debug print
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }, status=500)

@csrf_exempt
@require_POST
@login_required(login_url='/auth/login')
def create_reply(request, pk):
    question = get_object_or_404(Question, pk=pk)
    content = request.POST.get('content')
    if content:
        reply = Reply.objects.create(
            question=question,
            user=request.user,
            content=content
        )
        wib = timezone('Asia/Jakarta')
        return JsonResponse({
            'status': 'success',
            'reply': {
                'id': str(reply.pk),
                'user': reply.user.id,
                'content': reply.content,
                'created_at': reply.created_at.astimezone(wib).strftime("%d %b %Y, %H:%M WIB"),
                'updated_at': reply.updated_at.astimezone(wib).strftime("%d %b %Y, %H:%M WIB"),
                'username': reply.user.username,
                'question': str(question.pk)
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Content is required'}, status=400)

@csrf_exempt
@login_required(login_url='/auth/login')
@require_POST
def delete_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    
    if request.user == question.user or request.user.userprofile.role == "ADM":
        question.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

@csrf_exempt
@login_required(login_url='/auth/login')
@require_POST
def delete_reply(request, question_pk, reply_pk):
    reply = get_object_or_404(Reply, pk=reply_pk)
    question = get_object_or_404(Question, pk=question_pk)
    
    if (request.user == reply.user or 
        request.user == question.user or 
        request.user.userprofile.role == "ADM"):
        
        reply.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

@csrf_exempt
def forum_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    replies = Reply.objects.filter(question=question)
    
    user_id = request.user.id if request.user.is_authenticated else None
    is_admin = request.user.userprofile.role == "ADM" if request.user.is_authenticated else False

    return JsonResponse({
        'question': {
            'user': question.user.id,
            'title': question.title,
            'content': question.content,
            'created_at': question.created_at,
            'username': question.user.username,
            'category': question.category,
            'updated_at': question.updated_at,
            'reply_count': question.reply_set.count(),
            'car': str(question.car.pk) if question.car else None, 
        },
        'replies': [{
            'id': str(reply.pk), 
            'user': reply.user.id,
            'content': reply.content,
            'created_at': reply.created_at,
            'username': reply.user.username,
            'question': str(reply.question.pk),
        } for reply in replies],
        'permissions': {
            'user_id': user_id,
            'is_admin': is_admin
        }
    })