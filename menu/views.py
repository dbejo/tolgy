from collections import defaultdict
from decimal import Decimal
from io import BytesIO
from django.http import HttpResponse
from django.template import loader

from menu.models import Menu

from django.shortcuts import render, HttpResponse
import pandas as pd
import json
from django.db import transaction

from django.contrib.auth.decorators import login_required

# Create your views here.
def menu(request):
    menuitems = Menu.objects.all().order_by('category', 'price')
    grouped_menu = defaultdict(list)
    for item in menuitems:
        grouped_menu[item.category].append(item)
    template = loader.get_template('menu.html')
    context = {
        'grouped_menu': dict(grouped_menu)
    }
    return HttpResponse(template.render(context, request))

@login_required
def menu_modify(request):
    """ Handles menu upload, preview, confirmation, and rollback all in one view. """
    
    # If the user requests an export
    if request.method == "GET" and "export" in request.GET:
        return export_menu()

    # If a file is uploaded, process it
    if request.method == "POST" and "file" in request.FILES:
        uploaded_file = request.FILES["file"]
        
        if uploaded_file.name.endswith(".xlsx"):
            try:
                # Read Excel into DataFrame
                df = pd.read_excel(uploaded_file, engine="openpyxl")

                # Validate required columns
                required_columns = {"name", "ingredients", "category", "price"}
                if not required_columns.issubset(df.columns):
                    return render(request, "modify.html", {"error": "Missing required columns."})

                # Convert price to string for JSON serialization
                df["price"] = df["price"].apply(lambda x: format(float(x), ".2f") if isinstance(x, (Decimal, float)) else x)

                # Convert DataFrame to list of dictionaries
                menu_data = df.to_dict(orient="records")

                # Store preview in session
                request.session["menu_preview"] = json.dumps(menu_data)

                return render(request, "modify.html", {"menu_preview": menu_data})
            
            except Exception as e:
                return render(request, "modify.html", {"error": f"File processing error: {str(e)}"})

    # If user confirms update
    if request.method == "POST" and "confirm_update" in request.POST:
        menu_data = json.loads(request.session.get("menu_preview", "[]"))

        if not menu_data:
            return render(request, "modify.html", {"error": "No data to update."})

        uploaded_names = [item["name"] for item in menu_data]

        try:
            with transaction.atomic():
                # Store backup in session (for rollback)
                old_data = list(Menu.objects.values("name", "ingredients", "category", "price"))
                request.session["menu_backup"] = json.dumps(old_data)

                # Delete menu items that are not in uploaded file
                Menu.objects.exclude(name__in=uploaded_names).delete()

                # Update or create menu items
                for item in menu_data:
                    Menu.objects.update_or_create(
                        name=item["name"],  
                        defaults={
                            "ingredients": item.get("ingredients", ""),
                            "category": item.get("category", "Egyéb"),
                            "price": Decimal(item.get("price", 0)),  # Ensure price is Decimal
                        },
                    )

                # Clear session after update
                del request.session["menu_preview"]

            return render(request, "modify.html", {"success": "Menu updated successfully!"})
        
        except Exception as e:
            return render(request, "modify.html", {"error": f"Update failed: {str(e)}"})

    # If user triggers rollback
    if request.method == "POST" and "rollback" in request.POST:
        if "menu_backup" in request.session:
            try:
                old_data = json.loads(request.session["menu_backup"])

                # Convert price back to Decimal
                for item in old_data:
                    if "price" in item:
                        item["price"] = Decimal(item["price"])
                
                Menu.objects.all().delete()  # Clear current menu

                for item in old_data:
                    Menu.objects.create(**item)

                del request.session["menu_backup"]
                return render(request, "modify.html", {"success": "Rollback successful!"})
            
            except Exception as e:
                return render(request, "modify.html", {"error": f"Rollback failed: {str(e)}"})

    # Default: Render page with session data (preview if available)
    menu_preview = json.loads(request.session.get("menu_preview", "[]"))
    menu_backup = request.session.get("menu_backup")
    context = {
        "menu_preview": menu_preview,
        "menu_backup": menu_backup
        }
    return render(request, "modify.html", context)

def export_menu():
    """Exports the current menu as an Excel file."""
    menu_items = Menu.objects.all().values("name", "ingredients", "category", "price")

    if not menu_items:
        return HttpResponse("No menu data available.", content_type="text/plain")

    df = pd.DataFrame(menu_items)
    
    # Ensure price is formatted correctly
    df["price"] = df["price"].apply(lambda x: format(x, ".2f") if isinstance(x, Decimal) else x)

    # Create an in-memory Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Menu")

    output.seek(0)
    
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="menu.xlsx"'

    return response