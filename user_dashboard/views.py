from django.shortcuts import render, redirect
from authentication.models import UserProfile, UserRole
from review_rating.models import ReviewRating
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.http import JsonResponse
from django.templatetags.static import static
import cloudinary.uploader
import json
from django.core.paginator import Paginator, EmptyPage
from user_dashboard.forms import UpdateEmailForm, UpdateNameForm, UpdatePhoneForm

# Create your views here.
def user_dashboard(request) :
    return redirect("dashboard:biodata")

@login_required(login_url='/auth/login')
def user_biodata(request) :
    user = request.user
    user_profile = UserProfile.objects.get(user = user)
    user_role = user_profile.role

    if user_role == UserRole.BUYER or user_role == UserRole.SELLER or user_role == UserRole.ADMIN  :
        return render(request, 'biodata.html', {})
    else:
        return redirect('/auth/login')


@login_required(login_url='/auth/login')
def upload_profile_picture(request):
    if request.method == 'POST':
        profile = request.user.userprofile
        profile_picture_url = request.POST["profile_picture_url"]
        profile_picture_id = request.POST["profile_picture_id"]
        

        if profile.profile_picture_id:
            cloudinary.uploader.destroy(profile.profile_picture_id)

        profile.profile_picture = profile_picture_url
        profile.profile_picture_id = profile_picture_id

        profile.save()
        messages.success(request, 'Profile picture uploaded successfully!')

    return redirect("dashboard:biodata")

@login_required(login_url='/auth/login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Tetap login setelah password diubah
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard:biodata')  # Redirect setelah sukses
        else:
            messages.error(request, 'There was an error updating your password. Please try again.')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'change_password.html', {'form': form})

@login_required(login_url='/auth/login')
@csrf_exempt
@require_POST
def update_profile(request):
    if request.method == 'POST':
        user_profile = request.user.userprofile

        if 'name' in request.POST:
            user_profile.name = strip_tags(request.POST.get('name'))
            data = user_profile.name
        
        
        if 'email' in request.POST:
            validator = EmailValidator()
            email = strip_tags(request.POST.get('email'))
            try:
                validator(email)
                user_profile.email = email
                data = user_profile.email
            except ValidationError:
                return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

        if 'no_telp' in request.POST:
            user_profile.no_telp = strip_tags(request.POST.get('no_telp'))
            data = user_profile.no_telp

        # Simpan perubahan yang dilakukan
        user_profile.save()

        return JsonResponse({'status': 'success', 'message': 'Profile updated successfully', 'data': data})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required(login_url='/auth/login')
def rating_list(request):

    if request.user.userprofile.role != 'SEL':
        return redirect('/dashboard')
    
    daftar_review = {}
    page_obj = None
    if not request.user.userprofile.sellerprofile.reviews_received.exists():
        has_review = False
    else :
        daftar_review_seller = request.user.userprofile.sellerprofile.reviews_received.all()
        has_review = True

        page_number = request.GET.get('page', 1)
        paginator = Paginator(daftar_review_seller, 10)
        page_obj = paginator.get_page(page_number)

        for review in page_obj.object_list:

            if not review.reviewer.user_profile.profile_picture:
                reviewer_profile = static('user_dashboard/image/default-profile.png')
            else:
                reviewer_profile = review.reviewer.user_profile.profile_picture

            daftar_review[str(review.id)] = {
                'review' : review.review,
                'rating' : review.rating,
                'reviewer' : review.reviewer.user_profile.name,
                'reviewer_profile_pic' : reviewer_profile 
            }

    context = {
        'has_review' : has_review,
        'daftar_review' : daftar_review,
        'page_obj' : page_obj
    }

    return render(request, 'seller_rating_list.html', context)

@login_required(login_url='/auth/login')
def verifikasi_penjual(request):
    if request.user.userprofile.role != 'ADM':
        return redirect('/dashboard')
    
    if request.method == 'POST':
        try:
            verified_seller = UserProfile.objects.get(id=request.POST["idUser"])
            verified_seller.is_verified = True
            verified_seller.save()
            messages.success(request,"Berhasil Verifikasi Penjual")
            return redirect("dashboard:verifikasi_penjual")
        except:
            messages.error(request,"Gagal Verifikasi Penjual")
            return redirect("dashboard:verifikasi_penjual")

    unverified_seller_query = UserProfile.objects.filter(role='SEL', is_verified=False)
    page_number = request.GET.get('page', 1)
    paginator = Paginator(unverified_seller_query, 10)
    page_obj = paginator.get_page(page_number)
    
    if not unverified_seller_query.exists():
        unverified_seller = None
    else:
        page_number = request.GET.get('page')
        default_profile_pic = static('user_dashboard/image/default-profile.png')
        unverified_seller = {}

        for seller in page_obj.object_list:
            if not seller.profile_picture:
                seller_profile_picture = default_profile_pic
            else:
                seller_profile_picture =  seller.profile_picture

            unverified_seller[seller.id] = {
                'nama' : seller.name,
                'email' : seller.email,
                'profile_pic' : seller_profile_picture
            }

    context = {
        'unverified_seller' : unverified_seller,
        'page_obj' : page_obj
    }

    return render(request, 'adm_verifikasi_penjual.html', context)

@login_required(login_url='/auth/login')
@csrf_exempt
@require_POST
def get_user(request):
    try:
        data = json.loads(request.body)
        user = UserProfile.objects.get(id=data["id"])
        if not user.profile_picture:
            profile_pic = static('user_dashboard/image/default-profile.png')
        else:
            profile_pic = user.profile_picture

        if not user.is_verified:
            status = 'Menunggu Verifikasi'
        else:
            status = 'Sudah Verifikasi'

        return JsonResponse({
            'id' : user.id,
            'nama' : user.name,
            'email' : user.email,
            'no_telp' : user.no_telp,
            'role' : user.role,
            'profile_picture' : profile_pic,
            'status' : status,
        })
    except:
        return JsonResponse({"error": "User not found"}, status=404)
    
@csrf_exempt
@require_POST
def get_user_flutter(request):
    try:
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return JsonResponse({"status": "error", "message": "User is not authenticated"}, status=401)

            user = UserProfile.objects.get(user = request.user)

            if not user.profile_picture:
                profile_pic = ""
            else:
                profile_pic = user.profile_picture

            if not user.is_verified:
                status_akun = 'Menunggu Verifikasi'
            else:
                status_akun = 'Terverifikasi'

            return JsonResponse({
                'status' : 'success',
                'id' : user.id,
                'nama' : user.name,
                'email' : user.email,
                'no_telp' : user.no_telp,
                'role' : user.role,
                'profile_picture' : profile_pic,
                'status_akun' : status_akun,
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    except:
        return JsonResponse({"status": "error"}, status=404)

@csrf_exempt
@require_POST
def update_profile_flutter(request):
    try:
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return JsonResponse({"status": "error", "message": "User is not authenticated. Please re-log."}, status=401)
            
            user_profile = UserProfile.objects.get(user = request.user)
            data = json.loads(request.body)

            if 'name' in data:
                forms = UpdateNameForm(data=data, instance=user_profile)
                if forms.is_valid():
                    forms.save()
                    response = user_profile.name
                else:
                    return JsonResponse({'status': 'error', 'message': 'Nama tidak valid'}, status=400)
            
            
            if 'email' in data:
                forms = UpdateEmailForm(data=data, instance=user_profile)
                if forms.is_valid():
                    forms.save()
                    response = user_profile.email
                else:
                    return JsonResponse({'status': 'error', 'message': 'Email tidak valid'}, status=400)

            if 'no_telp' in data:
                forms = UpdatePhoneForm(data=data, instance=user_profile)
                if forms.is_valid():
                    forms.save()
                    response = user_profile.no_telp
                else:
                    return JsonResponse({'status': 'error', 'message': 'Nomor Telepon tidak valid'}, status=400)

            return JsonResponse({'status': 'success', 'message': 'Profile updated successfully', 'data': response}, status=200)

        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({"status": "error", 'message' : str(e)}, status=404)

@csrf_exempt
@require_POST
def change_password_flutter(request):
    try:
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return JsonResponse({"status": "error", "message": "User is not authenticated. Please re-log."}, status=401)

            user = request.user
            data = json.loads(request.body)
            form = PasswordChangeForm(user=user, data=data)

            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                return JsonResponse({"status": "success", "message": "Password updated successfully"}, status=200)
            else:
                return JsonResponse({"status": "error", "message": "Password not valid"}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
        
    except Exception as e:
        return JsonResponse({"status": "error", 'message' : str(e)}, status=404)
    
@csrf_exempt
@require_POST
def upload_profile_picture_flutter(request):
    try:
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return JsonResponse({"status": "error", "message": "User is not authenticated. Please re-log."}, status=401)
            
            data = json.loads(request.body)
            profile = UserProfile.objects.get(user = request.user)

            profile_picture_url = data["profile_picture_url"]
            profile_picture_id = data["profile_picture_id"]
            

            if profile.profile_picture_id:
                cloudinary.uploader.destroy(profile.profile_picture_id)


            profile.profile_picture = profile_picture_url
            profile.profile_picture_id = profile_picture_id

            profile.save()
            return JsonResponse({"status": "success", "message": "Profile picture uploaded successfully!"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", 'message' : str(e)}, status=404)

@csrf_exempt
def verifikasi_penjual_flutter(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "User is not authenticated. Please re-log."}, status=401)
        
        if request.user.userprofile.role != 'ADM':
            return JsonResponse({"status": "error", "message": "User is not authorized to access this page"}, status=403)
        
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                verified_seller = UserProfile.objects.get(id=data["idUser"])
                verified_seller.is_verified = True
                verified_seller.save()
                print("Berhasil Verifikasi Penjual id : ", data["idUser"])
                return JsonResponse({"status": "success", "message": "Berhasil Verifikasi Penjual"}, status=200)
            except Exception as e:
                print(e)
                return JsonResponse({"status": "error", "message": "Terjadi kesalahan pada saat proses verifikasi"}, status=400)

        unverified_seller_query = UserProfile.objects.filter(role='SEL', is_verified=False)
        page_number = request.GET.get("page")
        paginator = Paginator(unverified_seller_query.order_by('id') , 15)
        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            return JsonResponse({'status' : 'success', 'data' : None}, status=200)
        
        if not unverified_seller_query.exists():
            unverified_seller = None
        else:
            default_profile_pic = ""
            unverified_seller = {}

            for seller in page_obj.object_list:
                if not seller.profile_picture:
                    seller_profile_picture = default_profile_pic
                    seller_profile_picture_id = ""
                else:
                    seller_profile_picture =  seller.profile_picture
                    seller_profile_picture_id = seller.profile_picture_id

                unverified_seller[str(seller.id)] = {
                    'total_sales' : seller.sellerprofile.total_sales,
                    'rating' : seller.sellerprofile.rating,
                    'user_profile' : {
                        'name' : seller.name,
                        'email' : seller.email,
                        'no_telp' : seller.no_telp,
                        'role' : seller.role,
                        'profile_picture' : seller_profile_picture,
                        'profile_picture_id' : seller_profile_picture_id,
                        'is_verified' : seller.is_verified
                    }
                }   


        return JsonResponse({"status": "success", "data": unverified_seller}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"status": "error", 'message' : str(e)}, status=404)
    

def rating_list_flutter(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "User is not authenticated. Please re-log."}, status=401)
        
        if request.user.userprofile.role != 'SEL':
            return JsonResponse({"status": "error", "message": "User is not authorized to access this page"}, status=403)

        
        daftar_review = {}
        page_obj = None

        if not request.user.userprofile.sellerprofile.reviews_received.exists():
            has_review = 0
        else :
            has_review = 1
            daftar_review_seller = request.user.userprofile.sellerprofile.reviews_received.all()
            page_number = request.GET.get("page")
            paginator = Paginator(daftar_review_seller.order_by('created_at'), 15)
            page_obj = paginator.get_page(page_number)
            try:
                page_obj = paginator.page(page_number)
            except EmptyPage:
                data = {
                        'has_review' : 0,
                        'daftar_review' : daftar_review,
                    }
                return JsonResponse({'status' : 'success', 'data' : data}, status=200)


            for review in page_obj.object_list:
                if not review.reviewer.user_profile.profile_picture:
                    reviewer_profile = ""
                else:
                    reviewer_profile = review.reviewer.user_profile.profile_picture

                daftar_review[str(review.id)] = {
                    'review' : review.review,
                    'rating' : review.rating,
                    'reviewer' : review.reviewer.user_profile.name,
                    'created_at': review.created_at.strftime('%Y-%m-%d'),
                    'reviewer_profile_pic' : reviewer_profile 
                }


        data = {
            'has_review' : has_review,
            'daftar_review' : daftar_review,
        }

        return JsonResponse({'status' : 'success', 'data' : data}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", 'message' : str(e)}, status=404)