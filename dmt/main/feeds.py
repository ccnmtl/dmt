from django.conf import settings
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.template import loader
from django.utils.feedgenerator import Rss201rev2Feed
from .models import Node, StatusUpdate, Project, Item


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    """
    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs

    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)
        handler.addQuickElement(u'content:encoded', item['content_encoded'])


class ForumFeed(Feed):
    title = "PMT Forum"
    description = (
        "recent posts, personal log entries and comments in the forum"
        )

    def link(self):
        return settings.BASE_URL + "/forum/"

    def items(self):
        return Node.objects.order_by('-modified')[:10]

    def item_title(self, item):
        return item.subject

    def item_description(self, item):
        return (
            "<small>by <b><a href=\"%s%s"
            "\">%s</a></b> @ %s</small><br />%s") % (
                settings.BASE_URL,
                item.user.userprofile.get_absolute_url(),
                item.user.userprofile.get_fullname(), item.added, item.body)

    def item_link(self, item):
        return settings.BASE_URL + item.get_absolute_url()


class StatusUpdateFeed(Feed):
    feed_type = ExtendedRSSFeed
    title = "PMT Status Updates"
    description = "recent status updates"
    description_template = "feeds/status_item_description.html"

    def link(self):
        return settings.BASE_URL + "/status/"

    def items(self):
        return StatusUpdate.objects.order_by("-added")[:30]

    def item_link(self, item):
        return (settings.BASE_URL + item.project.get_absolute_url() +
                "#status-" + str(item.id))

    def item_author_name(self, item):
        return item.author.userprofile.get_fullname()

    def item_author_email(self, item):
        return item.author.userprofile.get_email()

    def item_pubdate(self, item):
        return item.added

    def item_extra_kwargs(self, item):
        description_tmp = loader.get_template(self.description_template)
        description = description_tmp.render(dict(obj=item), None)
        return {'content_encoded': description}


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
            (settings.BASE_URL +
             item.get_absolute_url()),
            item.title,
            item.status,
            item.owner_user.userprofile,
            item.assigned_user.userprofile,
            item.last_mod)
