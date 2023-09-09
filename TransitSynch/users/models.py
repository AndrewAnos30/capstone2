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
    middle_name = models.CharField(max_length=50, blank= True, null=True)
    status = models.CharField(max_length=100, choices=STATUS, default='Ordinary')
    gender = models.CharField(max_length=100, choices=GENDER,null=True, blank=False)
    age= models.PositiveIntegerField(null=True, blank=True)
    birthDate = models.DateField(null=True, blank=True)
    contactNumber= models.CharField(max_length=11, null=True, blank=True)
    emergencyContact= models.CharField(max_length=11,null=True, blank=True)
    contactPerson= models.CharField(max_length=100, null=True, blank=True)
    userSN= models.CharField(max_length=100, null=True, blank=True)
    balance= models.IntegerField(null=True, blank=True)
    DPA= models.BooleanField(default=False)
    graduation = models.DateField(null=True, blank=True)
    validID = models.ImageField(upload_to="valid_ids/", null=True, blank=True)
    QR = models.ImageField(upload_to="qrs/", null=True, blank=True)


    def __str__(self):
        return self.username

