import csv
import os

from django.conf import settings

from ..models import SenderPanel, SenderPanelItem, Utestid
from getresults_order.models import SenderModel


def load_sender_panels_from_csv(csv_filename=None):
    csv_filename = csv_filename or os.path.join(settings.BASE_DIR, 'testdata/sender_panels.csv')
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f, quotechar="'")
        header = next(reader)
        header = [h.lower() for h in header]
        for row in reader:
            r = dict(zip(header, row))
            try:
                sender_model = SenderModel.objects.get(name=r['sender_model'].strip())
            except SenderModel.DoesNotExist:
                sender_model = SenderModel.objects.create(name=r['sender_model'].strip())
            try:
                sender_panel = SenderPanel.objects.get(
                    name=r['sender_panel'].strip(),
                    sender_model=sender_model)
            except SenderPanel.DoesNotExist:
                sender_panel = SenderPanel.objects.create(
                    name=r['sender_panel'].strip(),
                    sender_model=sender_model)
            utestid = Utestid.objects.get(name=r['utestid'].strip())
            sender_utestid = r['sender_utestid'].strip()
            try:
                SenderPanelItem.objects.get(
                    sender_panel=sender_panel,
                    utestid=utestid,
                    sender_utestid=sender_utestid)
            except SenderPanelItem.DoesNotExist:
                SenderPanelItem.objects.create(
                    sender_panel=sender_panel,
                    utestid=utestid,
                    sender_utestid=sender_utestid)
