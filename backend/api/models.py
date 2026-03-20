from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email field must be set.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Client(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    liable = models.BooleanField(null=True, blank=True)
    liable_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name or self.email or f"Client {self.pk}"


class Case(models.Model):
    class Recommendation(models.TextChoices):
        ACCEPT = "ACCEPT", "Accept"
        REJECT = "REJECT", "Reject"
        REVIEW = "REVIEW", "Review"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CLOSED = "CLOSED", "Closed"

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="cases",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="cases",
    )
    incident_type = models.CharField(max_length=255, null=True, blank=True)
    incident_summary = models.TextField(null=True, blank=True)
    recommendation = models.CharField(
        max_length=10,
        choices=Recommendation.choices,
        null=True,
        blank=True,
    )
    recommendation_reason = models.TextField(null=True, blank=True)
    voice_note_url = models.URLField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Case {self.pk}"


class Damages(models.Model):
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="damages",
    )
    treatment_received = models.BooleanField(null=True, blank=True)
    treatment_type = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    treatment_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Damages {self.pk} for case {self.case_id}"


class Coverage(models.Model):
    class CoverageType(models.TextChoices):
        FIRST_PARTY = "FIRST_PARTY", "1st party"
        THIRD_PARTY = "THIRD_PARTY", "3rd party"

    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="coverages",
    )
    type = models.CharField(
        max_length=20,
        choices=CoverageType.choices,
        null=True,
        blank=True,
    )
    policy_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    deductible = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    insurer_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Coverage {self.pk} for case {self.case_id}"
