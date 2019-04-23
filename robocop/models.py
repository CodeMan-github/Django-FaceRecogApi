from django.db import models

class User(models.Model):
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=255)

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    
class Image(models.Model):
    fileName = models.CharField(max_length=255)
    values = models.CharField(max_length=1023)
    image = models.CharField(max_length=255)
    flag = models.CharField(max_length=10)