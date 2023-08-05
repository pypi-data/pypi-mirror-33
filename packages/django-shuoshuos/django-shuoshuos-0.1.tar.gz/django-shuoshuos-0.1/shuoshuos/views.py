from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .models import Shuoshuos
from django.utils import timezone

# Create your views here.

def index(request):
    latest_shuoshuo_list = Shuoshuos.objects.order_by('-pub_date')[:5]
    context = {
        'latest_shuoshuo_list': latest_shuoshuo_list,
    }
    return render(request, 'shuoshuos/index.html',context)
def detail(request, shuoshuo_id):
    shuoshuo=get_object_or_404(Shuoshuos,pk=shuoshuo_id)
    return render(request, 'shuoshuos/detail.html', {'shuoshuo': shuoshuo})
def vote(request,shuoshuo_id):
    if 'inputUserName' in request.POST:
        person = request.POST['inputUserName']
    else:
        person = "Not inputUserName"
    if 'inputShuoshuo' in request.POST:
        shuoshuotext = request.POST['inputShuoshuo']
    else:
        shuoshuotext = "Not inputShuoshuo"
    
    s=Shuoshuos(shuoshuo_person=person,shuoshuo_text=shuoshuotext,pub_date=timezone.now())
    s.save()
    return index(request)
