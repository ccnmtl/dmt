from django.forms import ModelForm
from .models import StatusUpdate


class StatusUpdateForm(ModelForm):
    class Meta:
        model = StatusUpdate
        fields = ['body']
