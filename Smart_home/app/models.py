from django.db import models

class Devices(models.Model):
    name = models.CharField(max_length=30)
    mac = models.CharField(max_length=17)
    device_id = models.IntegerField()
    localization = models.CharField(max_length=30, default='Not assigned')
    type = models.CharField(max_length=8)
    value = models.CharField(max_length=20)

    def __str__(self):
        return self.name