from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Client(models.Model):
    client_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Case(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"

    class Stage(models.TextChoices):
        INTAKE = "intake", "Intake"
        LOR = "LOR", "LOR"
        RECORD_GATHERING = "record_gathering", "Record Gathering"
        MMI_REACHED = "MMI_reached", "MMI Reached"
        DEMAND_PAGE_GENERATED = "demand_page_generated", "Demand Page Generated"

    STAGE_SEQUENCE = [
        Stage.INTAKE,
        Stage.LOR,
        Stage.RECORD_GATHERING,
        Stage.MMI_REACHED,
        Stage.DEMAND_PAGE_GENERATED,
    ]

    case_id = models.BigAutoField(primary_key=True)
    start_date = models.DateField()
    intake_date = models.DateField()
    incident_type = models.CharField(max_length=255)
    insurance_company_name = models.CharField(max_length=255)
    status = models.CharField(max_length=16, choices=Status.choices)
    stage = models.CharField(max_length=32, choices=Stage.choices)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="cases",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cases",
    )

    def __str__(self):
        return f"Case {self.case_id} - {self.client.name}"

    def get_next_stage(self):
        current_index = self.STAGE_SEQUENCE.index(self.stage)

        if current_index >= len(self.STAGE_SEQUENCE) - 1:
            return None

        return self.STAGE_SEQUENCE[current_index + 1]


class CaseLog(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    stage = models.CharField(max_length=32, choices=Case.Stage.choices)
    description = models.TextField()

    def __str__(self):
        return f"Log {self.log_id} for case {self.case.case_id}"
