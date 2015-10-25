import csv
import os

from django.conf import settings

from .models import Utestid, OrderPanel, OrderPanelItem


class Configure(object):

    def __init__(self, utestid_file=None, sender_file=None):
        self.utestid_filename = (
            utestid_file or os.path.join(settings.BASE_DIR, 'testdata/utestids.csv'))
        self.order_panel_file = sender_file or os.path.join(settings.BASE_DIR, 'testdata/order_panels.csv')
        self.load_all()

    def load_all(self):
        self.load_utestids_from_csv()
        self.load_order_panels_from_csv()

    def load_order_panels_from_csv(self):
        csv_filename = self.order_panel_file
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

    def load_utestids_from_csv(self):
        csv_filename = self.utestid_filename
        with open(csv_filename, 'r') as f:
            reader = csv.reader(f, quotechar="'")
            header = next(reader)
            header = [h.lower() for h in header]
            for row in reader:
                r = dict(zip(header, row))
                try:
                    Utestid.objects.get(name=r['name'].strip())
                except Utestid.DoesNotExist:
                    Utestid.objects.create(
                        name=r['name'].strip(),
                        description=r['description'].strip().lower(),
                        value_type=r['value_type'].lower(),
                        value_datatype=r['value_datatype'].lower(),
                        lower_limit=r['lower_limit'] if r['lower_limit'] else None,
                        upper_limit=r['upper_limit'] if r['upper_limit'] else None,
                        precision=r['precision'] if r['precision'] else None,
                        formula=r['formula'] if r['formula'] else None,
                        formula_utestid_name=r['formula_utestid_name'].lower() if r['formula_utestid_name'] else None,
                    )
