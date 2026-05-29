from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

class Login(AbstractUser):
    userType = models.CharField(max_length=50)  
    # admin / staff / volunteer / user
    viewPass = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username

class District(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=100, default="Kerala")

    def __str__(self):
        return self.name

class Citizen(models.Model):
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=300)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    profile_pic = models.ImageField(upload_to="citizen_profile", null=True, blank=True)
    status = models.CharField(max_length=40, default="active")

    def __str__(self):
        return self.name

class Staff(models.Model):
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(max_length=200)
    profile_pic = models.ImageField(upload_to="staff_profile", null=True, blank=True)
    status = models.CharField(max_length=40, default="active")

    def __str__(self):
        return self.name

class Volunteer(models.Model):
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.TextField(default="", help_text="e.g., First Aid, Swimming, Driving")
    availability_status = models.CharField(max_length=50, default="Available")
    profile_pic = models.ImageField(upload_to="volunteer_profile", null=True, blank=True)
    status = models.CharField(max_length=40, default="Pending") 

    def __str__(self):
        return self.name

class ResourceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.ImageField(upload_to="resource_icons", null=True, blank=True)

    def __str__(self):
        return self.name

class ResourceStock(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    unit = models.CharField(max_length=50, help_text="e.g., kg, liters, units")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item_name} ({self.district.name})"

class UserResourceRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
        ('Rejected', 'Rejected'),
    ]
    PRIORITY_CHOICES = [
        ('Critical', 'Critical'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    user = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE)
    quantity_needed = models.CharField(max_length=100)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    description = models.TextField()
    location_details = models.TextField()
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.name} Request by {self.user.name}"

class ResourceDistribution(models.Model):
    request = models.OneToOneField(UserResourceRequest, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.SET_NULL, null=True, blank=True)
    officer = models.ForeignKey(Staff, on_delete=models.CASCADE)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Distribution for Request #{self.request.id}"

class Notification(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"


class StaffResourceRequirement(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=200)
    quantity_needed = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_satisfied = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    unit = models.CharField(max_length=50, help_text="e.g., kg, packets, units")
    description = models.TextField()
    location_details = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, default='Open')  # 'Open' / 'Fulfilled'
    created_at = models.DateTimeField(auto_now_add=True)

    def remaining_needed(self):
        return max(0.0, float(self.quantity_needed) - float(self.quantity_satisfied))

    def __str__(self):
        return f"{self.item_name} Needed in {self.district.name}"


class DonationOffer(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Assigned', 'Volunteer Assigned'),
        ('Collected', 'Collected by Volunteer'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]
    requirement = models.ForeignKey(StaffResourceRequirement, on_delete=models.CASCADE)
    donor_login = models.ForeignKey(Login, on_delete=models.CASCADE)
    donor_name = models.CharField(max_length=200)
    donor_phone = models.CharField(max_length=20)
    donor_type = models.CharField(max_length=20)  # 'Citizen' / 'Volunteer'
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    need_assistance = models.BooleanField(default=False)
    pickup_address = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    assigned_volunteer = models.ForeignKey(Volunteer, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donation of {self.quantity} {self.requirement.unit} for {self.requirement.item_name}"

