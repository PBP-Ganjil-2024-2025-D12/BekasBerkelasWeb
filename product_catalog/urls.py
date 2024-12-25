from django.urls import path
from product_catalog.views import car_list, view_details_json, create_car, delete_car, mobil_saya, contact_seller, view_details, show_all_cars, create_car_flutter, show_user_profile_json, filter_cars, search_filter_cars,delete_flutter,get_seller_username, get_seller_contact, get_seller_verif, delete_flutter_admin

app_name = 'product_catalog'

urlpatterns = [
    path('', car_list, name='car_list'),
    path('carsjson/', show_all_cars, name='all-cars'),
    path('mobil_saya/', mobil_saya, name='mobil_saya'),
    path('create_car/', create_car, name='create_car'),
    path('delete_car/<uuid:car_id>/', delete_car, name='delete_car'),
    path('car/<uuid:car_id>/contact/', contact_seller, name='contact_seller'),
    path('detail/<uuid:car_id>/', view_details, name='view_details'),
    path('detail/json/<uuid:car_id>/', view_details_json, name='view_details_json'),
    path('create-flutter/', create_car_flutter, name='create_flutter'),
    path('api/user-profile/', show_user_profile_json, name='show_user_profile_json'),
    path('api/mobilsaya/', filter_cars, name='filter_cars'),
    path('api/cars/filter/', search_filter_cars, name='filter_cars_json'),
    path('api/mobilsaya/delete/', delete_flutter, name='delete_flutter'),
    path('api/get-seller-username/<uuid:car_id>/', get_seller_username, name='get-seller-username'),
    path('api/get-seller-contact/<uuid:car_id>/', get_seller_contact, name='get-seller-contact'),
    path('api/get-seller-verif/<str:username>/', get_seller_verif, name='get-seller-verif'),
    path('api/deleteAdmin', delete_flutter_admin, name='get-seller-delete_flutter_admin'),
]
