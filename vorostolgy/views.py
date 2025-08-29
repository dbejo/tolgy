from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from alert.models import Alert


def home(request):
    alerts = Alert.objects.active()
    return render(request, "home.html", {"alerts": alerts})

def contact(request):
    return render(request, "contact.html")

@login_required
def operator_admin(request):
    return render(request, "operator_admin.html")