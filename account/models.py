from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

UT_ADMIN = 1
UT_TYPE1 = 3
UT_UNKNOWN = 0

USER_TYPES = (
    (UT_ADMIN, "Admin"),
    (UT_TYPE1, "Patient"),
)


class UserManager(BaseUserManager):
    def create_user(self, email, u_type=UT_UNKNOWN, name=None, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=UserManager.normalize_email(email),
            name=name,
            type=u_type)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_type1_user(self, email, phone, name):
        user = self.create_user(email,
                                name=name,
                                u_type=UT_TYPE1)
        return user

    def create_superuser(self, email, password, name):
        user = self.create_user(email,
                                name=name,
                                u_type=UT_ADMIN,
                                password=password,)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    name = models.CharField(max_length=64)
    type = models.PositiveSmallIntegerField(choices=USER_TYPES, default=UT_UNKNOWN)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    @property
    def type_str(self):
        return [b for (a, b) in USER_TYPES if a == self.type][0]

    def get_full_name(self):
        # For this case we return email. Could also be User.first_name User.last_name if you have these fields
        return self.email

    def get_short_name(self):
        # For this case we return email. Could also be User.first_name if you have this field
        return self.email

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        # Handle whether the user has a specific permission?"
        return True

    def has_module_perms(self, app_label):
        # Handle whether the user has permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        # Handle whether the user is a member of staff?"
        return self.is_admin


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
