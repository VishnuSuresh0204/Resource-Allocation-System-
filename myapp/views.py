from myapp.models import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
from decimal import Decimal

# ================= PUBLIC VIEWS =================

def index(request):
    logout(request)
    return render(request, 'index.html')

def login_view(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            request.session["lid"] = user.id
            if user.userType == "admin" or user.is_superuser:
                return redirect("/admin_home")
            elif user.userType == "staff":
                s = Staff.objects.get(loginid=user)
                if s.status == "active": return redirect("/staff_home")
                messages.error(request, f"Account {s.status}")
            elif user.userType == "volunteer":
                v = Volunteer.objects.get(loginid=user)
                if v.status == "Approved": 
                    return redirect("/volunteer_home")
                elif v.status == "Blocked":
                    messages.error(request, "Your account has been blocked by the admin.")
                else:
                    messages.error(request, f"Account {v.status}. Wait for approval.")
            elif user.userType == "user":
                return redirect("/citizen_home")
            logout(request)
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')

def signout(request):
    logout(request)
    return redirect("/")

def register_citizen(request):
    if request.method == "POST":
        u, p, n, e, ph = request.POST.get('username'), request.POST.get('password'), request.POST.get('name'), request.POST.get('email'), request.POST.get('phone')
        ad, di, pic = request.POST.get('address'), request.POST.get('district'), request.FILES.get('profile_pic')
        if Login.objects.filter(username=u).exists():
            messages.error(request, "Username exists")
            return redirect("/register_citizen")
        log = Login.objects.create_user(username=u, password=p, userType="user", viewPass=p)
        Citizen.objects.create(loginid=log, name=n, email=e, phone=ph, address=ad, district_id=di, profile_pic=pic)
        messages.success(request, "Registered Successfully")
        return redirect("/login")
    return render(request, 'register_citizen.html', {'districts': District.objects.all()})

def register_volunteer(request):
    if request.method == "POST":
        u, p, n, e, ph = request.POST.get('username'), request.POST.get('password'), request.POST.get('name'), request.POST.get('email'), request.POST.get('phone')
        sk, di, pic = request.POST.get('skills'), request.POST.get('district'), request.FILES.get('profile_pic')
        if Login.objects.filter(username=u).exists():
            messages.error(request, "Username exists")
            return redirect("/register_volunteer")
        log = Login.objects.create_user(username=u, password=p, userType="volunteer", viewPass=p)
        Volunteer.objects.create(loginid=log, name=n, email=e, phone=ph, skills=sk, district_id=di, profile_pic=pic)
        messages.success(request, "Registration Success. Wait for Admin Approval.")
        return redirect("/login")
    return render(request, 'register_volunteer.html', {'districts': District.objects.all()})

# ================= ADMIN VIEWS =================

def admin_home(request):
    districts_qs = District.objects.all()
    districts_list = []
    for d in districts_qs:
        districts_list.append({
            'name': d.name,
            'staff_count': Staff.objects.filter(district=d).count(),
            'volunteer_count': Volunteer.objects.filter(district=d).count(),
        })
    return render(request, 'ADMIN/admin_home.html', {
        'districts': District.objects.count(),
        'staff': Staff.objects.count(),
        'volunteers': Volunteer.objects.count(),
        'districts_list': districts_list
    })

def admin_manage_districts(request):
    return render(request, 'ADMIN/manage_districts.html', {'districts': District.objects.all()})

def admin_add_district(request):
    if request.method == "POST":
        District.objects.create(name=request.POST.get('name'), description=request.POST.get('description'))
        messages.success(request, "District Added")
        return redirect("/admin_manage_districts")
    return render(request, 'ADMIN/add_district.html')

def admin_manage_staff(request):
    return render(request, 'ADMIN/manage_staff.html', {'staff': Staff.objects.all()})

def admin_add_staff(request):
    if request.method == "POST":
        u, p, n, e, ph = request.POST.get('username'), request.POST.get('password'), request.POST.get('name'), request.POST.get('email'), request.POST.get('phone')
        di, des, pic = request.POST.get('district'), request.POST.get('designation'), request.FILES.get('profile_pic')
        log = Login.objects.create_user(username=u, password=p, userType="staff", viewPass=p)
        Staff.objects.create(loginid=log, name=n, email=e, phone=ph, district_id=di, designation=des, profile_pic=pic)
        messages.success(request, "Staff Added")
        return redirect("/admin_manage_staff")
    return render(request, 'ADMIN/add_staff.html', {'districts': District.objects.all()})

def admin_approve_volunteers(request):
    return render(request, 'ADMIN/approve_volunteers.html', {'volunteers': Volunteer.objects.all()})

def admin_volunteer_action(request):
    v = Volunteer.objects.get(id=request.GET.get("id"))
    act = request.GET.get("act")
    if act == "reject": v.loginid.delete()
    else: 
        v.status = act
        v.save()
    messages.success(request, f"Volunteer {act}")
    return redirect("/admin_approve_volunteers")

def admin_edit_district(request):
    d = District.objects.get(id=request.GET.get("id"))
    if request.method == "POST":
        d.name = request.POST.get('name')
        d.description = request.POST.get('description')
        d.save()
        messages.success(request, "District Updated")
        return redirect("/admin_manage_districts")
    return render(request, 'ADMIN/edit_district.html', {'district': d})

def admin_delete_district(request):
    d = District.objects.get(id=request.GET.get("id"))
    d.delete()
    messages.success(request, "District Deleted")
    return redirect("/admin_manage_districts")

def admin_edit_staff(request):
    s = Staff.objects.get(id=request.GET.get("id"))
    if request.method == "POST":
        s.name = request.POST.get('name')
        s.email = request.POST.get('email')
        s.phone = request.POST.get('phone')
        s.designation = request.POST.get('designation')
        s.district_id = request.POST.get('district')
        pic = request.FILES.get('profile_pic')
        if pic:
            s.profile_pic = pic
        s.save()
        messages.success(request, "Staff Officer Updated")
        return redirect("/admin_manage_staff")
    return render(request, 'ADMIN/edit_staff.html', {'staff': s, 'districts': District.objects.all()})

def admin_staff_status(request):
    s = Staff.objects.get(id=request.GET.get("id"))
    act = request.GET.get("act")
    s.status = act
    s.save()
    messages.success(request, f"Officer {act.title()}")
    return redirect("/admin_manage_staff")


def admin_manage_resource_categories(request):
    return render(request, 'ADMIN/manage_resource_categories.html', {'categories': ResourceCategory.objects.all()})

def admin_add_resource_category(request):
    if request.method == "POST":
        ResourceCategory.objects.create(name=request.POST.get('name'), description=request.POST.get('description'), icon=request.FILES.get('icon'))
        messages.success(request, "Category Added")
        return redirect("/admin_manage_resource_categories")
    return render(request, 'ADMIN/add_resource_category.html')

def admin_edit_resource_category(request):
    c = ResourceCategory.objects.get(id=request.GET.get("id"))
    if request.method == "POST":
        c.name = request.POST.get('name')
        c.description = request.POST.get('description')
        icon = request.FILES.get('icon')
        if icon:
            c.icon = icon
        c.save()
        messages.success(request, "Category Updated")
        return redirect("/admin_manage_resource_categories")
    return render(request, 'ADMIN/edit_resource_category.html', {'category': c})

def admin_delete_resource_category(request):
    c = ResourceCategory.objects.get(id=request.GET.get("id"))
    c.delete()
    messages.success(request, "Category Deleted")
    return redirect("/admin_manage_resource_categories")

def admin_view_resource_stock(request):
    return render(request, 'ADMIN/view_resource_stock.html', {'stock': ResourceStock.objects.all().order_by('district')})

# ================= STAFF VIEWS =================

def staff_home(request):
    s = Staff.objects.get(loginid_id=request.session["lid"])
    if s.status != "active":
        messages.error(request, "Your account has been blocked or is inactive.")
        return redirect("/login")
    return render(request, 'STAFF/staff_home.html', {'staff': s})

def staff_manage_stock(request):
    s = Staff.objects.get(loginid_id=request.session["lid"])
    if s.status != "active":
        messages.error(request, "Your account has been blocked or is inactive.")
        return redirect("/login")
    return render(request, 'STAFF/manage_stock.html', {'stock': ResourceStock.objects.filter(district=s.district), 'staff': s})

def staff_add_stock(request):
    s = Staff.objects.get(loginid_id=request.session["lid"])
    if s.status != "active":
        messages.error(request, "Your account has been blocked or is inactive.")
        return redirect("/login")
    if request.method == "POST":
        it, qty, un = request.POST.get('item_name'), Decimal(request.POST.get('quantity')), request.POST.get('unit')
        stock, created = ResourceStock.objects.get_or_create(district=s.district, category_id=request.POST.get('category'), item_name=it, defaults={'unit': un})
        if not created: 
            stock.quantity += qty
            stock.save()
        messages.success(request, "Stock Updated")
        return redirect("/staff_manage_stock")
    return render(request, 'STAFF/add_stock.html', {'categories': ResourceCategory.objects.all()})

def staff_view_resource_requests(request):
    s = Staff.objects.get(loginid_id=request.session["lid"])
    if s.status != "active":
        messages.error(request, "Your account has been blocked or is inactive.")
        return redirect("/login")
    return render(request, 'STAFF/view_resource_requests.html', {'requests': UserResourceRequest.objects.filter(district=s.district).order_by('-requested_at'), 'staff': s})

def staff_approve_resource_request(request):
    s = Staff.objects.get(loginid_id=request.session["lid"])
    if s.status != "active":
        messages.error(request, "Your account has been blocked or is inactive.")
        return redirect("/login")
    r = UserResourceRequest.objects.get(id=request.GET.get("id"))
    if request.method == "POST":
        v_id = request.POST.get('volunteer')
        r.status = "Approved"
        r.save()
        ResourceDistribution.objects.create(request=r, volunteer_id=v_id, officer=s, remarks=request.POST.get('remarks'), dispatched_at=datetime.now())
        Notification.objects.create(user=Volunteer.objects.get(id=v_id).loginid, message=f"New Resource Delivery Assigned: {r.category.name}")
        messages.success(request, "Request Approved & Volunteer Assigned")
        return redirect("/staff_view_resource_requests")
    return render(request, 'STAFF/approve_resource_request.html', {'req': r, 'volunteers': Volunteer.objects.filter(district=s.district, status="Approved", availability_status="Available")})

# ================= CITIZEN VIEWS =================

def citizen_home(request):
    c = Citizen.objects.get(loginid_id=request.session["lid"])
    return render(request, 'CITIZEN/citizen_home.html', {'citizen': c})

def citizen_request_resource(request):
    c = Citizen.objects.get(loginid_id=request.session["lid"])
    if request.method == "POST":
        UserResourceRequest.objects.create(user=c, district=c.district, category_id=request.POST.get('category'), quantity_needed=request.POST.get('quantity'), priority=request.POST.get('priority'), description=request.POST.get('description'), location_details=request.POST.get('location'))
        messages.success(request, "Request Submitted Successfully")
        return redirect("/citizen_view_resource_requests")
    return render(request, 'CITIZEN/request_resource.html', {'categories': ResourceCategory.objects.all()})

def citizen_view_resource_requests(request):
    c = Citizen.objects.get(loginid_id=request.session["lid"])
    return render(request, 'CITIZEN/view_resource_requests.html', {'requests': UserResourceRequest.objects.filter(user=c).order_by('-requested_at')})


# ================= VOLUNTEER VIEWS =================

def volunteer_home(request):
    v = Volunteer.objects.get(loginid_id=request.session["lid"])
    if v.status != "Approved":
        messages.error(request, "Your account has been blocked or is no longer approved.")
        return redirect("/login")
    return render(request, 'VOLUNTEER/volunteer_home.html', {'volunteer': v, 'deliveries': ResourceDistribution.objects.filter(volunteer=v).exclude(request__status='Delivered')})

def volunteer_view_deliveries(request):
    v = Volunteer.objects.get(loginid_id=request.session["lid"])
    if v.status != "Approved":
        messages.error(request, "Your account has been blocked or is no longer approved.")
        return redirect("/login")
    return render(request, 'VOLUNTEER/view_deliveries.html', {'deliveries': ResourceDistribution.objects.filter(volunteer=v).order_by('-dispatched_at')})

def volunteer_update_delivery(request):
    v = Volunteer.objects.get(loginid_id=request.session["lid"])
    if v.status != "Approved":
        messages.error(request, "Your account has been blocked or is no longer approved.")
        return redirect("/login")
    d = ResourceDistribution.objects.get(id=request.GET.get("id"))
    if request.method == "POST":
        d.request.status = "Delivered"
        d.request.save()
        d.delivered_at = datetime.now()
        d.save()
        messages.success(request, "Delivery Completed")
    return redirect("/volunteer_view_deliveries")

def get_notifications(request):
    from django.http import JsonResponse
    nots = Notification.objects.filter(user_id=request.session.get("lid"), is_read=False)
    data = [{'message': n.message, 'id': n.id} for n in nots]
    nots.update(is_read=True)
    return JsonResponse({'notifications': data})
