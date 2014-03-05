from django.contrib.syndication.views import Feed
from .models import Node, StatusUpdate


class ForumFeed(Feed):
    title = "PMT Forum"
    link = "/forum/"
    description = (
        "recent posts, personal log entries and comments in the forum")

    def items(self):
        return Node.objects.order_by('-modified')[:10]

    def item_title(self, item):
        return item.subject

    def item_description(self, item):
        return (
            "<small>by <b><a href=\"https://dmt.ccnmtl.columbia.edu%s"
            "\">%s</a></b> @ %s</small><br />%s") % (
            item.author.get_absolute_url(),
            item.author.fullname, item.added, item.body)

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
            ("https://dmt.ccnmtl.columbia.edu"
             + item.project.get_absolute_url()),
            item.project.name,
            item.body,
            "https://dmt.ccnmtl.columbia.edu" + item.user.get_absolute_url(),
            item.user.fullname,
            item.added.date())
