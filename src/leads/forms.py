from django import forms

from .models import Lead


class ContactForm(forms.ModelForm):
    """نموذج التواصل العام: الاسم + (جوال أو بريد) + نص الرسالة."""

    class Meta:
        model = Lead
        fields = ["name", "phone", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "dir": "ltr"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "dir": "ltr"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # نوع الطلب ثابت قبل التحقق حتى يطبّق Lead.clean() قواعد التواصل العام.
        self.instance.lead_type = Lead.CONTACT
        self.fields["message"].required = True
