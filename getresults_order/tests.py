import math

from django.test import TestCase

from .models import Utestid, OrderPanelItem, BaseOrder, OrderPanel
from .utils import load_utestids_from_csv, load_order_panels_from_csv


class DummyOrder(BaseOrder):

    class Meta:
        app_label = 'getresults_order'


class TestGetresults(TestCase):

    def setUp(self):
        load_utestids_from_csv()
        load_order_panels_from_csv()

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

    def test_panel_item_string(self):
        """Asserts a string result is imported and formatted correctly."""
        order_panel = OrderPanel.objects.create(name='Elisa')
        utestid = Utestid.objects.create(
            name='ELISA',
            value_type='absolute',
            value_datatype='string')
        order_panel_item = OrderPanelItem.objects.create(
            order_panel=order_panel,
            utestid=utestid)
        value = order_panel_item.utestid.value('POS')
        self.assertEquals(value, 'POS')

    def test_panel_item_integer(self):
        """Asserts an integer result is imported and formatted correctly."""
        order_panel = OrderPanel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMH',
            value_type='absolute',
            value_datatype='integer',
        )
        order_panel_item = OrderPanelItem.objects.create(
            order_panel=order_panel,
            utestid=utestid,
        )
        value = order_panel_item.utestid.value(100.99)
        self.assertEquals(value, 101)

    def test_panel_item_decimal(self):
        """Asserts a decimal result is imported and formatted correctly."""
        order_panel = OrderPanel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMH',
            value_type='absolute',
            value_datatype='decimal',
            precision=1)
        order_panel_item = OrderPanelItem.objects.create(
            order_panel=order_panel,
            utestid=utestid)
        value = order_panel_item.utestid.value(100.77)
        self.assertEquals(value, 100.8)

    def test_panel_item_calc(self):
        """Asserts a calculated result is formatted correctly."""
        order_panel = OrderPanel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMHLOG',
            value_type='calculated',
            value_datatype='decimal',
            precision=2,
            formula='LOG10')
        order_panel_item = OrderPanelItem.objects.create(
            order_panel=order_panel,
            utestid=utestid)
        value = order_panel_item.utestid.value(750000)
        self.assertEquals(value, round(math.log10(750000), 2))

    def test_panel_item_formula(self):
        order_panel = OrderPanel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMHLOG',
            value_type='calculated',
            value_datatype='decimal',
            precision=2,
            formula='1 + log10(100)')
        order_panel_item = OrderPanelItem.objects.create(
            order_panel=order_panel,
            utestid=utestid,
        )
        self.assertRaises(ValueError, order_panel_item.utestid.value, 750000)

    def test_panel_item_quantifier_eq(self):
        order_panel = OrderPanel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMH',
            value_type='absolute',
            value_datatype='integer')
        order_panel_item = OrderPanelItem.objects.create(
            order_panel=order_panel,
            utestid=utestid
        )
        value_with_quantifier = order_panel_item.utestid.value_with_quantifier(1000)
        self.assertEquals(value_with_quantifier, ('=', 1000))

    def test_panel_item_quantifier_lt(self):
        order_panel = OrderPanel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMH',
            value_type='absolute',
            value_datatype='integer',
            lower_limit=400,
            upper_limit=750000)
        order_panel_item = OrderPanelItem.objects.create(
            order_panel=order_panel,
            utestid=utestid)
        value_with_quantifier = order_panel_item.utestid.value_with_quantifier(400)
        self.assertEquals(value_with_quantifier, ('=', 400))
        value_with_quantifier = order_panel_item.utestid.value_with_quantifier(399)
        self.assertEquals(value_with_quantifier, ('<', 400))

    def test_panel_item_quantifier_gt(self):
        order_panel = OrderPanel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMH',
            value_type='absolute',
            value_datatype='integer',
            lower_limit=400,
            upper_limit=750000)
        order_panel_item = OrderPanelItem.objects.create(
            order_panel=order_panel,
            utestid=utestid)
        value_with_quantifier = order_panel_item.utestid.value_with_quantifier(750000)
        self.assertEquals(value_with_quantifier, ('=', 750000))
        value_with_quantifier = order_panel_item.utestid.value_with_quantifier(750001)
        self.assertEquals(value_with_quantifier, ('>', 750000))
