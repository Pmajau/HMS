from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
        ('patient', 'Patient'),
    ]

    email           = models.EmailField(unique=True)
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100)
    role            = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number    = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    date_joined     = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    objects = UserManager()

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    # Helper properties for role checking
    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_doctor(self):
        return self.role == 'doctor'

    @property
    def is_nurse(self):
        return self.role == 'nurse'

    @property
    def is_receptionist(self):
        return self.role == 'receptionist'

    @property
    def is_patient(self):
        return self.role == 'patient'