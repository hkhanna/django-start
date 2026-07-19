import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone


class EmailFieldCaseInsensitive(models.EmailField):
    """Normalizes email case during cleaning."""

    def to_python(self, value):
        value = super().to_python(value)
        if value:
            return value.lower()
        else:
            return value


class UserManager(BaseUserManager):
    """Customized user manager"""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError("User must have an email address")
        email = email.lower()
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


class User(AbstractUser):
    """Customized User model"""

    uuid: models.UUIDField = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="UUID",
        help_text="Secondary ID",
    )
    username = None  # type: ignore
    email = EmailFieldCaseInsensitive(
        unique=True,  # Even though we have the constraint below, this is required because it is the USERNAME_FIELD.
        verbose_name="email address",
    )

    display_name: models.CharField = models.CharField(
        max_length=254,
        blank=True,
        help_text="The name that will be displayed by default to other users.",
    )
    date_joined = None  # type: ignore
    created_at: models.DateTimeField = models.DateTimeField(
        db_index=True, default=timezone.now
    )
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    objects = UserManager()  # type: ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list = []  # type: ignore

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="unique_email_case_insensitive",
            )
        ]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<User: {self.email} (#{self.id})>"

    @property
    def name(self):
        if self.display_name:
            return self.display_name
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email
