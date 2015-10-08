import csv
import os

from django.conf import settings

from ..models import SenderPanel, Sender, SenderModel


def load_senders_from_csv(csv_filename=None):
    csv_filename = csv_filename or os.path.join(settings.BASE_DIR, 'testdata/senders.csv')
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f, quotechar="'")
        header = next(reader)
        header = [h.lower() for h in header]
        for row in reader:
            r = dict(zip(header, row))
            serial_number = r['serial_number'].strip()
            try:
                Sender.objects.get(serial_number=serial_number)
            except Sender.DoesNotExist:
                sender_model = SenderModel.objects.get(name=r['sender_model'].strip())
                sender_panel = SenderPanel.objects.get(
                    name=r['sender_panel'].strip(),
                    sender_model=sender_model)
                Sender.objects.create(
                    serial_number=serial_number,
                    sender_panel=sender_panel,
                    sender_model=sender_model,
                )
