from django.urls import path
from wishlist.views import show_wishlist, add_to_wishlist, edit_wishlist, remove_from_wishlist, show_json, get_wishlist_item, get_wishlist_car_ids, add_wishlist_flutter, edit_wishlist_flutter, remove_wishlist_flutter

app_name = 'wishlist'

urlpatterns = [
    path('', show_wishlist, name='wishlist_page'),
    path('show_wishlist', show_wishlist, name='show_wishlist'),
    path('add/<uuid:car_id>', add_to_wishlist, name='add_to_wishlist'),
    path('edit/<uuid:wishlist_id>', edit_wishlist, name='edit_wishlist'),
    path('remove/<uuid:wishlist_id>', remove_from_wishlist, name='remove_from_wishlist'),
    path('json', show_json, name='show_json'),
    path('get_wishlist_item/<uuid:wishlist_id>/', get_wishlist_item, name='get_wishlist_item'),
    path('car_ids/', get_wishlist_car_ids, name='get_wishlist_car_ids'),
    path('add_wishlist/<uuid:car_id>/', add_wishlist_flutter, name='add_wishlist_flutter'),
    path('edit_wishlist/<uuid:wishlist_id>/', edit_wishlist_flutter, name='edit_wishlist_flutter'),
    path('remove_wishlist/<uuid:wishlist_id>/', remove_wishlist_flutter, name='remove_wishlist_flutter'),
]
