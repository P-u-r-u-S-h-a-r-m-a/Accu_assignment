from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self,email,name,password=None):
        """creates and saves a user with username and password"""
        if not email:
            raise ValueError("Users must have an email address")
        if not name:
            raise ValueError("Users must have a name")
        
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password)
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user




class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True)
    name=models.CharField( max_length=50)
    is_active=models.BooleanField(default=True)
    is_admin=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=["name"]
    def __str__(self):
        return self.email
    
    def get_name(self):
        return self.name
    
    def has_perm(self,perm,obj=None):
        "Does the user have a specific permission ?"
        return True
    
    def has_module_perms(self,app_label):
        "does the user have permissions to view app 'app_label'??"
        return True
    
    @property
    def is_staff(self):
        "Is the user staff"
        #all admins are treated as staff
        return self.is_admin


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['sender', 'receiver']