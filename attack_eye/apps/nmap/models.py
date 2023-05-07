from django.db import models

# Create your models here.
class port_scan(models.Model):
    UserId = models.CharField(max_length=70, blank=False, default='')
    domain = models.CharField(max_length=200,blank=False, default='')
    # published = models.BooleanField(default=False)
    published =  models.DateField(("DATE"), auto_now_add=True)
    timeDateStart = models.DateTimeField(("DATE"), auto_now_add=True)
    timeDateEnd = models.CharField(max_length=70,blank=False, default='')
    pending = models.IntegerField()
    
    class Meta:
        app_label = 'nmap'