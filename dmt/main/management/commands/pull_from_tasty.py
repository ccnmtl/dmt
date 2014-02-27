from django.core.management.base import BaseCommand
from dmt.main.models import Item, Node
import requests
from json import loads


class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **kwargs):
        r = requests.get("http://tasty.ccnmtl.columbia.edu/service/pmt/")
        data = loads(r.text)
        print str(data.keys())
        # [u'items', u'user_item_tags', u'users', u'tags']
        for user, item, tag in data['user_item_tags']:
            print user['user'], item['item'], tag['tag']
            if item['item'].startswith('item_'):
                iid = item['item'].split('_')[1]
                try:
                    i = Item.objects.get(iid=iid)
                    i.tags.add(tag['tag'][:99])
                except Item.DoesNotExist:
                    continue
            if item['item'].startswith('node_'):
                nid = item['item'].split('_')[1]
                try:
                    n = Node.objects.get(nid=nid)
                    n.tags.add(tag['tag'][:99])
                except Node.DoesNotExist:
                    continue
