"""
Database models for the accounts app.

The single model here is a custom ``User`` that authenticates with **email +
password** (instead of Django's default username + password). This matches the
task's "login with email and password" requirement and is the modern best
practice for SaaS-style apps.

Why a custom user?
------------------
Django's built-in ``auth.User`` forces a ``username`` field and a 30-char limit
on email. By providing our own model and setting
``AUTH_USER_MODEL = "accounts.User"`` in settings.py, we get:
  * email as the unique login identifier,
  * first/last name fields,
  * an is_active / is_staff flag set we control.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Manager for the User model.

    A *manager* is the object through which you query/create model instances
    (like a repository class). ``BaseUserManager`` adds password-hashing helpers
    (``create_user`` / ``create_superuser``) which we override to make ``email``
    required instead of ``username``.
    """

    def create_user(self, email: str, password: str = "", **extra_fields):
        """Create and save a regular user with an email and password."""
        if not email:
            raise ValueError("Users must have an email address.")
        # normalize_email lowercases the domain part (User@Ex.COM -> User@ex.com).
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # set_password() hashes the plaintext password using Django's hasher
        # (PBKDF2 by default) so we NEVER store plaintext.
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str = "", **extra_fields):
        """Create and save a superuser (staff + superuser flags)."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Email-based custom user model.

    Inherits:
      * AbstractBaseUser -> provides ``password`` + ``last_login`` fields and
        password-checking logic (check_password, set_password).
      * PermissionsMixin -> adds ``is_superuser`` and the groups/permissions
        many-to-many fields.

    We do NOT inherit from ``auth.User`` because that would clash with our
    custom model; Django only allows one user model per project.
    """

    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80, blank=True)

    # Flags. is_active=False disables login (soft delete / ban).
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # admin site access

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Tell Django which field is the unique login identifier.
    USERNAME_FIELD = "email"
    # Fields prompted for when running `python manage.py createsuperuser`.
    REQUIRED_FIELDS: list[str] = ["first_name", "last_name"]

    # Wire the manager above so User.objects.create_user(...) works.
    objects = UserManager()

    class Meta:
        ordering = ["-created_at"]
        db_table = "users"

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        """Convenience: "First Last" (trimmed if either is blank)."""
        return f"{self.first_name} {self.last_name}".strip()
