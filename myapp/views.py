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
    pending_volunteers = Volunteer.objects.filter(status="Pending").count()
    pending_requests = UserResourceRequest.objects.filter(status="Pending").count()
    total_requests = UserResourceRequest.objects.count()
    delivered_requests = UserResourceRequest.objects.filter(status="Delivered").count()
    categories_count = ResourceCategory.objects.count()
    citizens_count = Citizen.objects.count()
    recent_requests = UserResourceRequest.objects.order_by('-requested_at')[:5]
    return render(request, 'ADMIN/admin_home.html', {
        'districts': District.objects.count(),
        'staff': Staff.objects.count(),
        'volunteers': Volunteer.objects.count(),
        'districts_list': districts_list,
        'pending_volunteers': pending_volunteers,
        'pending_requests': pending_requests,
        'total_requests': total_requests,
        'delivered_requests': delivered_requests,
        'categories_count': categories_count,
        'citizens_count': citizens_count,
        'recent_requests': recent_requests,
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
        
    # Gather statistics
    total_stock_items = ResourceStock.objects.filter(district=s.district).count()
    pending_requests = UserResourceRequest.objects.filter(district=s.district, status='Pending').count()
    active_requirements = StaffResourceRequirement.objects.filter(district=s.district, status='Open').count()
    pending_donations = DonationOffer.objects.filter(requirement__district=s.district, status='Pending').count()
    district_volunteers = Volunteer.objects.filter(district=s.district, status='Approved').count()
    
    recent_requests = UserResourceRequest.objects.filter(district=s.district).order_by('-requested_at')[:5]
    recent_donations = DonationOffer.objects.filter(requirement__district=s.district).order_by('-created_at')[:5]
    
    return render(request, 'STAFF/staff_home.html', {
        'staff': s,
        'total_stock_items': total_stock_items,
        'pending_requests': pending_requests,
        'active_requirements': active_requirements,
        'pending_donations': pending_donations,
        'district_volunteers': district_volunteers,
        'recent_requests': recent_requests,
        'recent_donations': recent_donations,
    })

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
    
    # Gather statistics
    my_active_requests = UserResourceRequest.objects.filter(user=c, status__in=['Pending', 'Approved', 'Dispatched']).count()
    my_completed_donations = DonationOffer.objects.filter(donor_login=c.loginid, status='Completed').count()
    my_pending_donations = DonationOffer.objects.filter(donor_login=c.loginid, status='Pending').count()
    open_requirements = StaffResourceRequirement.objects.filter(district=c.district, status='Open').count()
    
    recent_requests = UserResourceRequest.objects.filter(user=c).order_by('-requested_at')[:5]
    recent_donations = DonationOffer.objects.filter(donor_login=c.loginid).order_by('-created_at')[:5]
    
    return render(request, 'CITIZEN/citizen_home.html', {
        'citizen': c,
        'my_active_requests': my_active_requests,
        'my_completed_donations': my_completed_donations,
        'my_pending_donations': my_pending_donations,
        'open_requirements': open_requirements,
        'recent_requests': recent_requests,
        'recent_donations': recent_donations,
    })

def citizen_request_resource(request):
    c = Citizen.objects.get(loginid_id=request.session["lid"])
    if request.method == "POST":
        UserResourceRequest.objects.create(
            user=c, district=c.district, category_id=request.POST.get('category'), 
            quantity_needed=request.POST.get('quantity'), priority=request.POST.get('priority'), 
            description=request.POST.get('description'), location_details=request.POST.get('location'),
            latitude=request.POST.get('latitude'), longitude=request.POST.get('longitude')
        )
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
        
    # Gather statistics
    pending_deliveries = ResourceDistribution.objects.filter(volunteer=v).exclude(request__status='Delivered').count()
    assigned_pickups = DonationOffer.objects.filter(assigned_volunteer=v, status__in=['Assigned', 'Collected']).count()
    my_donations = DonationOffer.objects.filter(donor_login=v.loginid).count()
    open_requirements = StaffResourceRequirement.objects.filter(district=v.district, status='Open').count()
    
    recent_deliveries = ResourceDistribution.objects.filter(volunteer=v).order_by('-dispatched_at')[:5]
    recent_pickups = DonationOffer.objects.filter(assigned_volunteer=v).order_by('-created_at')[:5]
    
    return render(request, 'VOLUNTEER/volunteer_home.html', {
        'volunteer': v,
        'deliveries': ResourceDistribution.objects.filter(volunteer=v).exclude(request__status='Delivered'),
        'pending_deliveries_count': pending_deliveries,
        'assigned_pickups_count': assigned_pickups,
        'my_donations_count': my_donations,
        'open_requirements_count': open_requirements,
        'recent_deliveries': recent_deliveries,
        'recent_pickups': recent_pickups,
    })

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


# ================= STAFF RESOURCE REQUIREMENTS VIEWS =================

def staff_add_requirement(request):
    s = Staff.objects.get(loginid_id=request.session["lid"])
    if s.status != "active":
        messages.error(request, "Your account has been blocked or is inactive.")
        return redirect("/login")
    if request.method == "POST":
        category_id = request.POST.get('category')
        item_name = request.POST.get('item_name')
        quantity_needed = request.POST.get('quantity_needed')
        unit = request.POST.get('unit')
        description = request.POST.get('description')
        
        StaffResourceRequirement.objects.create(
            staff=s,
            district=s.district,
            category_id=category_id,
            item_name=item_name,
            quantity_needed=Decimal(quantity_needed),
            unit=unit,
            description=description,
            location_details=request.POST.get('location_details'),
            latitude=request.POST.get('latitude'),
            longitude=request.POST.get('longitude')
        )
        messages.success(request, "Resource Requirement Added successfully")
        return redirect("/staff_view_requirements")
    
    categories = ResourceCategory.objects.all()
    return render(request, 'STAFF/add_requirement.html', {'categories': categories, 'staff': s})


def staff_view_requirements(request):
    s = Staff.objects.get(loginid_id=request.session["lid"])
    if s.status != "active":
        messages.error(request, "Your account has been blocked or is inactive.")
        return redirect("/login")
    requirements = StaffResourceRequirement.objects.filter(district=s.district).order_by('-created_at')
    return render(request, 'STAFF/view_requirements.html', {'requirements': requirements, 'staff': s})


def staff_view_donations(request):
    s = Staff.objects.get(loginid_id=request.session["lid"])
    if s.status != "active":
        messages.error(request, "Your account has been blocked or is inactive.")
        return redirect("/login")
    donations = DonationOffer.objects.filter(requirement__district=s.district).order_by('-created_at')
    volunteers = Volunteer.objects.filter(district=s.district, status="Approved", availability_status="Available")
    return render(request, 'STAFF/view_donations.html', {'donations': donations, 'volunteers': volunteers, 'staff': s})


def complete_donation(donation):
    if donation.status != 'Completed':
        donation.status = 'Completed'
        donation.save()
        
        # Update requirement satisfied quantity
        req = donation.requirement
        req.quantity_satisfied = Decimal(str(req.quantity_satisfied)) + Decimal(str(donation.quantity))
        if req.quantity_satisfied >= req.quantity_needed:
            req.status = 'Fulfilled'
        req.save()
        
        # Update ResourceStock in the district
        stock, created = ResourceStock.objects.get_or_create(
            district=req.district,
            category=req.category,
            item_name=req.item_name,
            defaults={'unit': req.unit, 'quantity': Decimal('0.0')}
        )
        if not created:
            stock.quantity = Decimal(str(stock.quantity)) + Decimal(str(donation.quantity))
            stock.save()
        else:
            stock.quantity = Decimal(str(donation.quantity))
            stock.save()

        # Notify donor
        Notification.objects.create(
            user=donation.donor_login,
            message=f"Your donation of {donation.quantity} {req.unit} of {req.item_name} has been completed and added to stock."
        )


def staff_approve_donation(request):
    s = Staff.objects.get(loginid_id=request.session["lid"])
    if s.status != "active":
        messages.error(request, "Your account has been blocked or is inactive.")
        return redirect("/login")
    if request.method == "POST":
        d_id = request.POST.get('id')
        act = request.POST.get('act')
        donation = DonationOffer.objects.get(id=d_id)
        if act == "assign":
            v_id = request.POST.get('volunteer')
            donation.assigned_volunteer_id = v_id
            donation.status = 'Assigned'
            donation.save()
            Notification.objects.create(
                user=donation.assigned_volunteer.loginid,
                message=f"New Donation Pickup Assigned: {donation.requirement.item_name}"
            )
            messages.success(request, "Volunteer Assigned successfully")
        elif act == "approve_direct":
            complete_donation(donation)
            messages.success(request, "Donation Approved and added to Stock")
        elif act == "reject":
            donation.status = 'Rejected'
            donation.save()
            messages.success(request, "Donation Rejected")
        return redirect("/staff_view_donations")


# ================= CITIZEN RESOURCE REQUIREMENTS & DONATIONS VIEWS =================

def citizen_view_requirements(request):
    c = Citizen.objects.get(loginid_id=request.session["lid"])
    requirements = StaffResourceRequirement.objects.filter(district=c.district).order_by('-created_at')
    # Filter only those that are not fulfilled to see if we can still donate
    for r in requirements:
        r.remaining = r.remaining_needed()
    return render(request, 'CITIZEN/view_requirements.html', {'requirements': requirements, 'citizen': c})


def citizen_donate(request):
    c = Citizen.objects.get(loginid_id=request.session["lid"])
    if request.method == "POST":
        req_id = request.POST.get('req_id')
        quantity = request.POST.get('quantity')
        need_assistance = request.POST.get('need_assistance') == 'on'
        pickup_address = request.POST.get('pickup_address')
        
        req = StaffResourceRequirement.objects.get(id=req_id)
        qty = Decimal(quantity)
        
        if qty <= 0:
            messages.error(request, "Quantity must be greater than zero.")
            return redirect(f"/citizen_donate/?id={req_id}")
            
        remaining = Decimal(str(req.remaining_needed()))
        if qty > remaining:
            messages.error(request, "Quantity cannot exceed the remaining needed quantity.")
            return redirect(f"/citizen_donate/?id={req_id}")
            
        DonationOffer.objects.create(
            requirement=req,
            donor_login=c.loginid,
            donor_name=c.name,
            donor_phone=c.phone,
            donor_type='Citizen',
            quantity=qty,
            need_assistance=need_assistance,
            pickup_address=pickup_address,
            latitude=request.POST.get('latitude'),
            longitude=request.POST.get('longitude'),
            status='Pending'
        )
        messages.success(request, "Donation Offer submitted successfully.")
        return redirect("/citizen_view_donations")
        
    req_id = request.GET.get('id')
    req = StaffResourceRequirement.objects.get(id=req_id)
    req.remaining = req.remaining_needed()
    return render(request, 'CITIZEN/donate.html', {'req': req, 'citizen': c})


def citizen_view_donations(request):
    c = Citizen.objects.get(loginid_id=request.session["lid"])
    donations = DonationOffer.objects.filter(donor_login=c.loginid).order_by('-created_at')
    return render(request, 'CITIZEN/view_donations.html', {'donations': donations, 'citizen': c})


# ================= VOLUNTEER RESOURCE REQUIREMENTS & DONATIONS VIEWS =================

def volunteer_view_requirements(request):
    v = Volunteer.objects.get(loginid_id=request.session["lid"])
    if v.status != "Approved":
        messages.error(request, "Your account has been blocked or is no longer approved.")
        return redirect("/login")
    requirements = StaffResourceRequirement.objects.filter(district=v.district).order_by('-created_at')
    for r in requirements:
        r.remaining = r.remaining_needed()
    return render(request, 'VOLUNTEER/view_requirements.html', {'requirements': requirements, 'volunteer': v})


def volunteer_donate(request):
    v = Volunteer.objects.get(loginid_id=request.session["lid"])
    if v.status != "Approved":
        messages.error(request, "Your account has been blocked or is no longer approved.")
        return redirect("/login")
    if request.method == "POST":
        req_id = request.POST.get('req_id')
        quantity = request.POST.get('quantity')
        need_assistance = request.POST.get('need_assistance') == 'on'
        pickup_address = request.POST.get('pickup_address')
        
        req = StaffResourceRequirement.objects.get(id=req_id)
        qty = Decimal(quantity)
        
        if qty <= 0:
            messages.error(request, "Quantity must be greater than zero.")
            return redirect(f"/volunteer_donate/?id={req_id}")
            
        remaining = Decimal(str(req.remaining_needed()))
        if qty > remaining:
            messages.error(request, "Quantity cannot exceed the remaining needed quantity.")
            return redirect(f"/volunteer_donate/?id={req_id}")
            
        DonationOffer.objects.create(
            requirement=req,
            donor_login=v.loginid,
            donor_name=v.name,
            donor_phone=v.phone,
            donor_type='Volunteer',
            quantity=qty,
            need_assistance=need_assistance,
            pickup_address=pickup_address,
            latitude=request.POST.get('latitude'),
            longitude=request.POST.get('longitude'),
            status='Pending'
        )
        messages.success(request, "Donation Offer submitted successfully.")
        return redirect("/volunteer_view_donations")
        
    req_id = request.GET.get('id')
    req = StaffResourceRequirement.objects.get(id=req_id)
    req.remaining = req.remaining_needed()
    return render(request, 'VOLUNTEER/donate.html', {'req': req, 'volunteer': v})


def volunteer_view_donations(request):
    v = Volunteer.objects.get(loginid_id=request.session["lid"])
    if v.status != "Approved":
        messages.error(request, "Your account has been blocked or is no longer approved.")
        return redirect("/login")
    donations = DonationOffer.objects.filter(donor_login=v.loginid).order_by('-created_at')
    return render(request, 'VOLUNTEER/view_donations.html', {'donations': donations, 'volunteer': v})


def volunteer_assigned_donations(request):
    v = Volunteer.objects.get(loginid_id=request.session["lid"])
    if v.status != "Approved":
        messages.error(request, "Your account has been blocked or is no longer approved.")
        return redirect("/login")
    donations = DonationOffer.objects.filter(assigned_volunteer=v).order_by('-created_at')
    return render(request, 'VOLUNTEER/assigned_donations.html', {'donations': donations, 'volunteer': v})


def volunteer_update_donation(request):
    v = Volunteer.objects.get(loginid_id=request.session["lid"])
    if v.status != "Approved":
        messages.error(request, "Your account has been blocked or is no longer approved.")
        return redirect("/login")
    if request.method == "POST":
        d_id = request.POST.get('id')
        act = request.POST.get('act')
        donation = DonationOffer.objects.get(id=d_id, assigned_volunteer=v)
        
        if act == "Collected":
            donation.status = 'Collected'
            donation.save()
            Notification.objects.create(
                user=donation.requirement.staff.loginid,
                message=f"Volunteer {v.name} has collected the donation of {donation.quantity} {donation.requirement.unit} of {donation.requirement.item_name}."
            )
            messages.success(request, "Donation status updated to Collected.")
        elif act == "Completed":
            complete_donation(donation)
            messages.success(request, "Donation status updated to Completed and Stock updated.")
            
        return redirect("/volunteer_assigned_donations")
