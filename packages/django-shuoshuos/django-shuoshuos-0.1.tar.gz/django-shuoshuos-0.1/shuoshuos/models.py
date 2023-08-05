from django.db import models

# Create your models here.
class Shuoshuos(models.Model):
    shuoshuo_person=models.CharField(max_length=20)
    shuoshuo_text=models.CharField(max_length=900)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.shuoshuo_text
