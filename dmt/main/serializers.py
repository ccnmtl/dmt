from .models import User, Client, Project, Milestone, Item
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'fullname', 'email', 'status',
                  'type', 'title', 'phone', 'bio', 'photo_url',
                  'photo_width', 'photo_height', 'campus',
                  'building', 'room')


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
        fields = ('client_id', 'lastname', 'firstname', 'title',
                  'registration_date', 'department', 'school',
                  'add_affiliation', 'phone', 'email', 'contact',
                  'comments', 'status', 'email_secondary',
                  'phone_mobile', 'phone_other', 'website_url')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ('pid', 'name', 'pub_view', 'caretaker',
                  'description', 'status', 'type', 'area',
                  'url', 'restricted', 'approach', 'info_url',
                  'entry_rel', 'eval_url', 'projnum', 'scale',
                  'distrib', 'poster', 'wiki_category')


class MilestoneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Milestone
        fields = ('mid', 'name', 'target_date', 'project', 'status',
                  'description')


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Item
        fields = ('iid', 'type', 'owner', 'assigned_to', 'title',
                  'milestone', 'status', 'description', 'priority',
                  'r_status', 'last_mod', 'target_date', 'estimated_time',
                  'url')
