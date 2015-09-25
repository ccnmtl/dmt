from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from .models import Node, StatusUpdate, Project, Item


class ForumFeed(Feed):
    title = "PMT Forum"
    link = "/forum/"
    description = (
        "recent posts, personal log entries and comments in the forum"
        )

    def items(self):
        return Node.objects.order_by('-modified')[:10]

    def item_title(self, item):
        return item.subject

    def item_description(self, item):
        return (
            "<small>by <b><a href=\"https://dmt.ccnmtl.columbia.edu%s"
            "\">%s</a></b> @ %s</small><br />%s") % (
            item.user.userprofile.get_absolute_url(),
            item.user.userprofile.fullname, item.added, item.body)

    def item_link(self, item):
        return "https://dmt.ccnmtl.columbia.edu" + item.get_absolute_url()


class StatusUpdateFeed(Feed):
    title = "PMT Status Updates"
    link = "/status/"
    description = "recent status updates"

    def items(self):
        return StatusUpdate.objects.order_by("-added")[:30]

    def item_description(self, item):
        return """<a href="%s">%s</a>:  %s  -- <a href="%s">%s</a>  (%s)""" % (
            ("https://dmt.ccnmtl.columbia.edu" +
             item.project.get_absolute_url()),
            item.project.name,
            item.body,
            "https://dmt.ccnmtl.columbia.edu" + item.user.get_absolute_url(),
            item.user.fullname,
            item.added.date())


class ProjectFeed(Feed):
    """Create a feed of the active items, per project (id)"""

    # Looks up the project based on the pk id specified in the url
    def get_object(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        return project

    def title(self, obj):
        return "PMT Project Feed: %s" % obj.name

    def link(self, obj):
        return obj.url

    def description(self, obj):
        return "Recent project activity"

    def items(self, obj):
        # write a custom query here insetead of using project method,
        # since we care about the order
        active_pmt_items = Item.objects.filter(milestone__project=obj,
                                               status__in=['OPEN',
                                                           'RESOLVED',
                                                           'INPROGRESS']
                                               ).order_by('last_mod')
        return active_pmt_items

    def item_title(self, item):
        return "%s (%s)" % (item.title, item.status)

    def item_description(self, item):
        return """<a href="%s">%s</a>:  %s -- %s / assigned to: %s (%s)""" % (
            ("https://dmt.ccnmtl.columbia.edu" +
             item.get_absolute_url()),
            item.title,
            item.status,
            item.owner,
            item.assigned_to,
            item.last_mod)
