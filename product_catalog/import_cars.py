import os
import csv
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BebasBerkelas.settings')


django.setup()

from product_catalog.models import Car 

def import_cars(csv_file_path):
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            car = Car(
                car_name=row['car_name'],
                brand=row['brand'],
                year=int(row['year']),
                mileage=int(row['mileage']),
                location=row['location'],
                transmission=row['transmission'],
                plate_type=row['plate type'],
                rear_camera=row['rear camera'] == '1',
                sun_roof=row['sun roof'] == '1',
                auto_retract_mirror=row['auto retract mirror'] == '1', 
                electric_parking_brake=row.get('electric parking brake') == '1',
                map_navigator=row.get('map navigator') == '1',
                vehicle_stability_control=row.get('vehicle stability control') == '1',
                keyless_push_start=row.get('keyless push start') == '1', 
                sports_mode=row.get('sports mode') == '1',
                camera_360_view=row.get('360 camera view') == '1', 
                power_sliding_door=row.get('power sliding door') == '1',
                auto_cruise_control=row.get('auto cruise control') == '1',
                price=float(row['price (Rp)']),
                instalment=float(row['instalment (Rp|Monthly)']),
            )
            car.save()
            print(f'Successfully added car: {car.car_name}')

if __name__ == "__main__":
    import_cars('filtered_car_data.csv')
