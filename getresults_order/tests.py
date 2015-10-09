from django.test import TestCase

from .models import Sender, SenderPanelItem
from .utils import (load_sender_panels_from_csv, load_utestids_from_csv, load_order_panels_from_csv,
                    load_senders_from_csv)

from getresults_order.models import BaseOrder, OrderPanel


class DummyOrder(BaseOrder):

    class Meta:
        app_label = 'getresults_order'


class TestGetresults(TestCase):

    def setUp(self):
        load_utestids_from_csv()
        load_sender_panels_from_csv()
        load_order_panels_from_csv()
        load_senders_from_csv()

    def test_find_sender_panel_items_from_serial_number(self):
        serial_number = 'E12334567890'
        sender = Sender.objects.get(serial_number=serial_number)
        self.assertEqual(sender.sender_panel.name, 'CD3/CD8/CD45/CD4 TruC')
        utestids = [i.utestid.name for i in SenderPanelItem.objects.filter(
            sender_panel=sender.sender_panel)]
        utestids.sort()
        self.assertEqual(utestids, ['CD4', 'CD4%', 'CD8', 'CD8%'])
        sender_utestids = [i.sender_utestid for i in SenderPanelItem.objects.filter(
            sender_panel=sender.sender_panel)]
        sender_utestids.sort()
        self.assertEqual(sender_utestids, [
            '(Average) CD3+CD4+ Abs Cnt',
            '(Average) CD3+CD8+ %Lymph',
            '(Average) CD3+CD8+ Abs Cnt',
            'CD3/CD8/CD45/CD4 TruC CD3+CD4+ %Lymph']
        )

    def test_order_creates_order_identifier(self):
        order_panel = OrderPanel.objects.create(name='panel1')
        order1 = DummyOrder.objects.create(
            aliquot_identifier='12345678',
            order_panel=order_panel)
        self.assertFalse(order1.order_identifier == '')
        self.assertFalse(order1.order_identifier is None)
        order2 = DummyOrder.objects.create(
            aliquot_identifier='12345678',
            order_panel=order_panel)
        self.assertTrue(order2.order_identifier)
        self.assertNotEqual(order1.order_identifier, order2.order_identifier)
