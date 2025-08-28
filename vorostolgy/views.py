from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, "home.html")

def contact(request):
    return render(request, "contact.html")

@login_required
def operator_admin(request):
    return render(request, "operator_admin.html")