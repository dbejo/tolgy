from django.shortcuts import redirect, render
from django.utils import timezone
from datetime import timedelta

from alert.models import Alert

# Create your views here.
def alert(request):
    alerts = Alert.objects.order_by('-valid_until')
    return render(request, "alert.html", {"alerts": alerts})

def alert_new(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        valid_until = request.POST.get('valid_until')
        Alert.objects.create(title=title, message=message, valid_until=valid_until)
        return redirect("alert")
    return render(request, "form.html")

def alert_extend(request, pk):
    alert = Alert.objects.get(pk=pk)
    if request.method == 'POST':
        days = int(request.POST.get('days'))
        if alert.valid_until:
            if alert.is_active():
                alert.valid_until += timedelta(days=days)
            else:
                alert.valid_until = timezone.now() + timedelta(days=days)
        else:
            alert.valid_until = timezone.now() + timedelta(days=days)
        alert.save()
    return redirect("alert")

def alert_deactivate(request, pk):
    alert = Alert.objects.get(pk=pk)
    if request.method == 'POST':
        alert.valid_until = timezone.now()
        alert.save()
    return redirect("alert")