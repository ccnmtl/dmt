from django.contrib.syndication.views import Feed
from .models import Node


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
