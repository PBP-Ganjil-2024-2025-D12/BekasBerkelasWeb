from django.urls import path
from forum.views import show_forum, create_question, create_reply, delete_reply, delete_question, get_questions_json, forum_detail

app_name = 'forum'

urlpatterns = [
    path('', show_forum, name='show_forum'),
    path('create_question/', create_question, name='create_question'),
    path('<uuid:pk>/', forum_detail, name='forum_detail'),
    path('<uuid:pk>/create_reply/', create_reply, name='create_reply'),
    path('<uuid:question_pk>/delete_reply/<uuid:reply_pk>/', delete_reply, name='delete_reply'),
    path('<uuid:pk>/delete_question/', delete_question, name='delete_question'),
    path('get_questions_json/', get_questions_json, name='get_questions_json'),
]