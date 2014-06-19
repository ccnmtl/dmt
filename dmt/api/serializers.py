from dmt.main.models import (
    Client, Item, Milestone, Project, User
)

from rest_framework import serializers


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
        fields = ('client_id', 'lastname', 'firstname', 'title',
                  'registration_date', 'department', 'school',
                  'add_affiliation', 'phone', 'email', 'contact',
                  'comments', 'status', 'email_secondary',
                  'phone_mobile', 'phone_other', 'website_url')


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    notifies = serializers.RelatedField(many=True)

    class Meta:
        model = Item
        fields = ('iid', 'title', 'type', 'owner', 'assigned_to',
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


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    milestone_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='milestone-detail')

    class Meta:
        model = Project
        fields = ('pid', 'name', 'pub_view', 'caretaker',
                  'description', 'status', 'type', 'area',
                  'url', 'restricted', 'approach', 'info_url',
                  'entry_rel', 'eval_url', 'projnum', 'scale',
                  'distrib', 'poster', 'wiki_category',
                  'milestone_set')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'fullname', 'email', 'status',
                  'type', 'title', 'phone', 'bio', 'photo_url',
                  'photo_width', 'photo_height', 'campus',
                  'building', 'room')
