from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):

    STATUS = (
        ('PWD', 'PWD'),
        ('Student', 'Student'),
        ('National Athlete', 'National Athlete'),
        ('Senior', 'Senior'),
        ('Ordinary', 'Ordinary')
    )

    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('LGBTQ+', 'Others')
    )

    email = models.EmailField(unique=True)
    status = models.CharField(max_length=100, choices=STATUS, default='Ordinary')
    description = models.TextField('Description', max_length=600, default='', null=True, blank=True)
    gender = models.CharField(max_length=100, choices=GENDER,null=True, blank=False)
    age= models.PositiveIntegerField(null=True, blank=True)
    birthDate = models.DateTimeField(null=True, blank=True)
    contactNumber= models.IntegerField(null=True, blank=True)
    emergencyContact= models.IntegerField(null=True, blank=True)
    contactPerson= models.CharField(max_length=100, null=True, blank=True)
    validID= models.ImageField(null=True, blank=True)
    userSN= models.CharField(max_length=100, null=True, blank=True)
    QR= models.ImageField(upload_to="image", null=True, blank=True)
    balance= models.IntegerField(null=True, blank=True)
    DPA= models.BooleanField(default=False)

    def __str__(self):
        return self.username