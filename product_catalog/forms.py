from django import forms
from .models import Car

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'car_name', 'brand', 'year', 'mileage', 'location', 'transmission', 'plate_type',
            'rear_camera', 'sun_roof', 'auto_retract_mirror', 'electric_parking_brake',
            'map_navigator', 'vehicle_stability_control', 'keyless_push_start', 'sports_mode',
            'camera_360_view', 'power_sliding_door', 'auto_cruise_control', 'price', 'instalment','image_url'
        ]
        widgets = {
            'image_url': forms.HiddenInput()
        }
class CarFilterForm(forms.Form):
    car_name = forms.CharField(max_length=100, required=False)
    brand = forms.CharField(max_length=100, required=False)
    year = forms.IntegerField(required=False)
    mileage = forms.IntegerField(required=False)
    location = forms.CharField(max_length=100, required=False)
    transmission = forms.ChoiceField(choices=[('', 'Any')] + list(Car.CAR_TRANSMISSION_CHOICES), required=False)
    plate_type = forms.ChoiceField(choices=[('', 'Any')] + list(Car.PLATE_TYPE_CHOICES), required=False)
    rear_camera = forms.BooleanField(required=False)
    sun_roof = forms.BooleanField(required=False)
    auto_retract_mirror = forms.BooleanField(required=False)
    electric_parking_brake = forms.BooleanField(required=False)
    map_navigator = forms.BooleanField(required=False)
    vehicle_stability_control = forms.BooleanField(required=False)
    keyless_push_start = forms.BooleanField(required=False)
    sports_mode = forms.BooleanField(required=False)
    camera_360_view = forms.BooleanField(required=False)
    power_sliding_door = forms.BooleanField(required=False)
    auto_cruise_control = forms.BooleanField(required=False)
    price_min = forms.DecimalField(max_digits=15, decimal_places=2, required=False)
    price_max = forms.DecimalField(max_digits=15, decimal_places=2, required=False)
    instalment_min = forms.DecimalField(max_digits=15, decimal_places=2, required=False)
    instalment_max = forms.DecimalField(max_digits=15, decimal_places=2, required=False)
