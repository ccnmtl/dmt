from django.forms import ModelForm
from .models import StatusUpdate, Node, User


class StatusUpdateForm(ModelForm):
    class Meta:
        model = StatusUpdate
        fields = ['body']


class NodeUpdateForm(ModelForm):
    class Meta:
        model = Node
        fields = ['subject', 'body']


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ["fullname", "email", "type", "title", "phone",
                  "bio", "photo_url", "photo_width", "photo_height",
                  "campus", "building", "room"]
