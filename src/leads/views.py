from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactForm


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "تم استلام رسالتك بنجاح، وسنتواصل معك قريبًا.")
            return redirect("leads:contact")
    else:
        form = ContactForm()
    return render(request, "pages/contact.html", {"form": form})
