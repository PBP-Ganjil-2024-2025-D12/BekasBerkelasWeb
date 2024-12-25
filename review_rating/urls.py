from django.urls import path
from review_rating.views import show_profile, add_review, show_json, show_reviews, delete_review, show_user_json, add_review_flutter, delete_review_flutter

app_name = 'review_rating'

urlpatterns = [
    path('<str:username>/', show_profile, name='show_profile'),
    path('<str:username>/add_review/', add_review, name='add_review'),
    path('<str:username>/add_review_flutter/', add_review_flutter, name='add_review_flutter'),
    path('<str:username>/add_review_flutter/', add_review_flutter, name='add_review_flutter'),
    path('<str:username>/show_json/', show_json, name='show_json'),
    path('<str:username>/show_user_json/', show_user_json, name='show_user_json'),
    path('<str:username>/reviews/', show_reviews, name='show_reviews'),
    path('delete_review/<uuid:review_id>/', delete_review, name='delete_review'),
    path('<str:username>/add_review_flutter/', add_review_flutter, name='add_review_flutter'),
    path('delete_review_flutter/<uuid:review_id>/', delete_review_flutter, name='delete_review_flutter'),
]