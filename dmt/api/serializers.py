from django.contrib.auth.models import User
from dmt.main.models import (
    Client, Item, Milestone, Notify, Project, UserProfile
)

from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
        fields = ('client_id', 'lastname', 'firstname', 'title',
                  'registration_date', 'department', 'school',
                  'add_affiliation', 'phone', 'email',
                  'comments', 'status', 'email_secondary',
                  'phone_mobile', 'phone_other', 'website_url')


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    notifies = serializers.StringRelatedField(many=True)
    owner_user = UserSerializer()
    assigned_user = UserSerializer()

    class Meta:
        model = Item
        fields = ('iid', 'title', 'type', 'owner_user', 'assigned_user',
                  'milestone', 'status', 'description', 'priority',
                  'r_status', 'last_mod', 'target_date', 'estimated_time',
                  'url', 'notifies')


class MilestoneSerializer(serializers.HyperlinkedModelSerializer):
    item_set = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='item-detail')

    class Meta:
        model = Milestone
        fields = ('mid', 'name', 'target_date', 'project', 'status',
                  'description', 'item_set')


class NotifySerializer(serializers.HyperlinkedModelSerializer):
    item = serializers.PrimaryKeyRelatedField(read_only=True)
    user = UserSerializer()

    class Meta:
        model = Notify
        fields = ('item', 'user')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    milestone_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='milestone-detail',
        read_only=True
    )
    caretaker_user = UserSerializer()

    class Meta:
        model = Project
        fields = ('pid', 'name', 'pub_view', 'caretaker_user',
                  'description', 'status', 'type', 'area',
                  'url', 'restricted', 'approach', 'info_url',
                  'entry_rel', 'eval_url', 'projnum', 'scale',
                  'distrib', 'poster', 'wiki_category',
                  'milestone_set')


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'fullname', 'email', 'status',
                  'type', 'title', 'phone', 'bio', 'photo_url',
                  'photo_width', 'photo_height', 'campus',
                  'building', 'room')
