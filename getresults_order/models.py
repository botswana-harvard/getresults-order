import ast

from math import log10

from django.db import models
from django.utils import timezone

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_constants.constants import PENDING
from getresults_aliquot.models import Aliquot

from .choices import VALUE_DATATYPES, VALUE_TYPES
from .order_identifier import OrderIdentifier


class OrderPanel(BaseUuidModel):

    name = models.CharField(
        max_length=50,
        unique=True
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'getresults_order'
        db_table = 'getresults_orderpanel'
        ordering = ('name', )


class Requisition(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    requisition_identifier = models.CharField(max_length=25)

    requisition_datetime = models.DateTimeField(null=True)

    specimen_identifier = models.CharField(
        max_length=25,
        help_text='if different from requisition identifier')

    specimen_type = models.CharField(max_length=25)

    tests = models.ManyToManyField(OrderPanel)

    class Meta:
        app_label = 'getresults_order'
        db_table = 'getresults_requisition'
        ordering = ('requisition_identifier', )


class BaseOrder(BaseUuidModel):

    order_identifier = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
    )

    order_datetime = models.DateTimeField(default=timezone.now)

    order_panel = models.ForeignKey(OrderPanel)

    aliquot_identifier = models.CharField(max_length=25)

    status = models.CharField(
        max_length=25, default=PENDING)

    history = HistoricalRecords()

    def __str__(self):
        return '{}: {}'.format(self.order_identifier, self.order_panel)

    def save(self, *args, **kwargs):
        order_identifier = OrderIdentifier()
        self.order_identifier = self.order_identifier or next(order_identifier)
        super(BaseOrder, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class Order(BaseOrder):

    aliquot = models.ForeignKey(Aliquot, null=True, editable=False)

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.order_identifier = self.order_identifier or OrderIdentifier(None)
        self.aliquot = Aliquot.objects.get(aliquot_identifier=self.aliquot_identifier)
        super(Order, self).save(*args, **kwargs)

    class Meta:
        app_label = 'getresults_order'
        db_table = 'getresults_order'
        ordering = ('order_identifier', )


class Utestid(BaseUuidModel):

    name = models.CharField(
        max_length=10,
        unique=True
    )

    description = models.CharField(
        max_length=50,
    )

    value_type = models.CharField(
        max_length=25,
        choices=VALUE_TYPES,
    )
    value_datatype = models.CharField(
        max_length=25,
        choices=VALUE_DATATYPES,
    )

    lower_limit = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='lower limit of detection (exclusive)'
    )

    upper_limit = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='upper limit of detection (exclusive)'
    )

    precision = models.IntegerField(
        null=True,
        blank=True,
    )

    formula = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        help_text='if a calculated value, include an a simple formula or LOG10')

    formula_utestid_name = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text='formula is based on the value of this utestid'
    )

    units = models.CharField(
        max_length=10,
        null=True
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def value(self, raw_value, value_type=None):
        """Returns the value as the type defined in value_type."""
        value_type = value_type or self.value_type
        if self.value_type == 'calculated':
            raw_value = self.calculated_value(raw_value)
        if self.value_datatype == 'string':
            return str(raw_value)
        elif self.value_datatype == 'integer':
            return int(round(float(raw_value), 0))
        elif self.value_datatype == 'decimal':
            return round(float(raw_value), self.precision)
        else:
            raise ValueError('Invalid utestid.value_type. Got \'{}\''.format(value_type))
        return None

    def calculated_value(self, raw_value):
        """Returns the value as the type defined in value_type.

        Formulas may use basic operators such as 1 + 1 that can be evaluted
        by ast.literla_eval.

        Allowed functions (so far):
            LOG10: if the formula is 'LOG10', the returned value will be log10 of value.
        """
        try:
            value = ast.literal_eval(self.formula.format(value=raw_value))
        except ValueError:
            if self.formula == 'LOG10':
                value = log10(float(raw_value))
            else:
                raise ValueError('Invalid formula for caluclated value. See {}')
        return value

    def value_with_quantifier(self, raw_value):
        """Returns a tuple of (quantifier, value) given a raw value.

        For example:
            * If the lower limit of detection is 400, a value of 400 returns ('=', 400)
              and a value of 399 returns ('<', 400).
            * if the upper limit of detection is 750000, a value of 750000 returns ('=', 750000)
              and a value of 750001 returns ('>', 750000)
        """
        value = self.value(raw_value)
        try:
            if value < self.lower_limit:
                return ('<', self.value(self.lower_limit, 'absolute'))
            elif value > self.upper_limit:
                return ('>', self.value(self.upper_limit, 'absolute'))
        except TypeError:
            pass
        return ('=', value)

    class Meta:
        app_label = 'getresults_order'
        db_table = 'getresults_utestid'
        ordering = ('name', )


class OrderPanelItem(BaseUuidModel):
    """Model that represents one item in an order panel.

    Has methods to format absolute values and to calculate, then format,
    calculated values. Lower and Upper limits of detection determine the
    quantifier.

    For example:
        * If the lower limit of detection is 400, a value of 400 returns ('=', 400)
          and a value of 399 returns ('<', 400).
        * if the upper limit of detection is 750000, a value of 750000 returns ('=', 750000)
          and a value of 750001 returns ('>', 750000)
    """
    order_panel = models.ForeignKey(OrderPanel)

    utestid = models.ForeignKey(Utestid)

    history = HistoricalRecords()

    def __str__(self):
        return '{}: {}'.format(self.utestid.name, self.order_panel.name)

    class Meta:
        app_label = 'getresults_order'
        db_table = 'getresults_orderpanelitem'
        unique_together = (('order_panel', 'utestid'), )
        ordering = ('order_panel', 'utestid')


class SenderModel(BaseUuidModel):

    """A class for the model or make of a sending device, e.g. FACSCalibur."""

    name = models.CharField(
        max_length=25,
        unique=True
    )

    make = models.CharField(
        max_length=25,
        null=True,
    )

    description = models.CharField(
        max_length=100,
        null=True
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'getresults_order'
        db_table = 'getresults_sendermodel'
        ordering = ('name', )


class SenderPanel(BaseUuidModel):

    """A class for the panel of results associated with a sending model/make."""

    name = models.CharField(max_length=25, unique=True)

    sender_model = models.ForeignKey(SenderModel)

    history = HistoricalRecords()

    def __str__(self):
        return '{}: {}'.format(self.sender_model.name, self.name)

    class Meta:
        app_label = 'getresults_order'
        db_table = 'getresults_senderpanel'
        ordering = ('name', )
        unique_together = ('sender_model', 'name')


class SenderPanelItem(BaseUuidModel):

    """A class for each item in a sending device's panel linking the field name from the device to a utestid."""

    sender_panel = models.ForeignKey(SenderPanel)

    utestid = models.ForeignKey(Utestid)

    sender_utestid = models.CharField(max_length=25)

    history = HistoricalRecords()

    def str(self):
        return '{} <--> {}'.format(self.sender_panel.name, self.utestid.name)

    class Meta:
        app_label = 'getresults_order'
        db_table = 'getresults_senderpanelitem'
        unique_together = ('sender_panel', 'utestid')


class Sender(BaseUuidModel):

    """A class for a specific sender device identified by serial number that links to a sender panel."""

    sender_model = models.ForeignKey(SenderModel)

    serial_number = models.CharField(
        max_length=25,
        unique=True
    )

    sender_panel = models.ForeignKey(SenderPanel)

    class Meta:
        app_label = 'getresults_order'
        db_table = 'getresults_sender'
        ordering = ('serial_number', )
