from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Public URLs
    path('', views.index),
    path('login/', views.login_view),
    path('logout/', views.signout),
    path('register_citizen/', views.register_citizen),
    path('register_volunteer/', views.register_volunteer),

    # Admin URLs
    path('admin_home/', views.admin_home),
    path('admin_manage_districts/', views.admin_manage_districts),
    path('admin_add_district/', views.admin_add_district),
    path('admin_edit_district/', views.admin_edit_district),
    path('admin_delete_district/', views.admin_delete_district),
    path('admin_manage_staff/', views.admin_manage_staff),
    path('admin_add_staff/', views.admin_add_staff),
    path('admin_edit_staff/', views.admin_edit_staff),
    path('admin_staff_status/', views.admin_staff_status),
    path('admin_approve_volunteers/', views.admin_approve_volunteers),
    path('admin_volunteer_action/', views.admin_volunteer_action),
    path('admin_manage_resource_categories/', views.admin_manage_resource_categories),
    path('admin_add_resource_category/', views.admin_add_resource_category),
    path('admin_edit_resource_category/', views.admin_edit_resource_category),
    path('admin_delete_resource_category/', views.admin_delete_resource_category),
    path('admin_view_resource_stock/', views.admin_view_resource_stock),

    # Staff URLs
    path('staff_home/', views.staff_home),
    path('staff_manage_stock/', views.staff_manage_stock),
    path('staff_add_stock/', views.staff_add_stock),
    path('staff_view_resource_requests/', views.staff_view_resource_requests),
    path('staff_approve_resource_request/', views.staff_approve_resource_request),

    # Citizen URLs
    path('citizen_home/', views.citizen_home),
    path('citizen_request_resource/', views.citizen_request_resource),
    path('citizen_view_resource_requests/', views.citizen_view_resource_requests),

    # Volunteer URLs
    path('volunteer_home/', views.volunteer_home),
    path('volunteer_view_deliveries/', views.volunteer_view_deliveries),
    path('volunteer_update_delivery/', views.volunteer_update_delivery),
    
    # Notifications
    path('get_notifications/', views.get_notifications),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
