import csv
import os

from django.conf import settings

from ..models import OrderPanel
from getresults_order.models import OrderPanelItem, Utestid


def load_order_panels_from_csv(csv_filename=None):
    csv_filename = csv_filename or os.path.join(settings.BASE_DIR, 'testdata/order_panels.csv')
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f, quotechar="'")
        header = next(reader)
        header = [h.lower() for h in header]
        for row in reader:
            r = dict(zip(header, row))
            try:
                order_panel = OrderPanel.objects.get(name=r['order_panel'].strip())
            except OrderPanel.DoesNotExist:
                order_panel = OrderPanel.objects.create(name=r['order_panel'].strip())
            try:
                utestid = Utestid.objects.get(name=r['utestid'].strip())
                OrderPanelItem.objects.get(order_panel=order_panel, utestid=utestid)
            except OrderPanelItem.DoesNotExist:
                OrderPanelItem.objects.create(order_panel=order_panel, utestid=utestid)
