from django.contrib import admin
from .models import Shuoshuos

# Register your models here.
class ShuoshuosAdmin(admin.ModelAdmin):
    list_display=('shuoshuo_person','shuoshuo_text','pub_date')
    search_fields = ['shuoshuo_text']

#admin.site.register(ShuoshuosAdmin)
admin.site.register(Shuoshuos,ShuoshuosAdmin)
