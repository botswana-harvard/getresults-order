import ast

from math import log10

from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords

from getresults_aliquot.models import Aliquot

from .choices import VALUE_DATATYPES, VALUE_TYPES


class Panel(BaseUuidModel):

    name = models.CharField(
        max_length=50,
        unique=True
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'getresults'
        ordering = ('name', )


class Order(BaseUuidModel):

    order_identifier = models.CharField(
        max_length=50,
        unique=True,
    )

    order_datetime = models.DateTimeField(null=True)

    panel = models.ForeignKey(Panel)

    aliquot = models.ForeignKey(Aliquot)

    specimen_identifier = models.CharField(
        max_length=50,
    )

    action_code = models.CharField(
        max_length=1,
        null=True)

    report_type = models.CharField(
        max_length=1,
        null=True)

    history = HistoricalRecords()

    def __str__(self):
        return '{}: {}'.format(self.order_identifier, self.panel)

    class Meta:
        app_label = 'getresults'
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
        app_label = 'getresults'
        ordering = ('name', )


class PanelItem(BaseUuidModel):
    """Model that represents one item in a panel.

    Has methods to format absolute values and to calculate, then format,
    calculated values. Lower and Upper limits of detection determine the
    quantifier.

    For example:
        * If the lower limit of detection is 400, a value of 400 returns ('=', 400)
          and a value of 399 returns ('<', 400).
        * if the upper limit of detection is 750000, a value of 750000 returns ('=', 750000)
          and a value of 750001 returns ('>', 750000)
    """
    panel = models.ForeignKey(Panel)

    utestid = models.ForeignKey(Utestid)

    history = HistoricalRecords()

    def __str__(self):
        return '{}: {}'.format(self.utestid.name, self.panel.name)

    class Meta:
        app_label = 'getresults'
        unique_together = ('panel', 'utestid')
        ordering = ('panel', 'utestid')


class Sender(BaseUuidModel):

    name = models.CharField(
        max_length=25,
        unique=True
    )

    description = models.CharField(
        max_length=100,
        null=True
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'getresults'
        db_table = 'getresults_sender'
        ordering = ('name', )


class UtestidMapping(BaseUuidModel):

    sender = models.ForeignKey(Sender)

    panel = models.ForeignKey(Panel)

    utestid = models.ForeignKey(Utestid)

    sender_utestid_name = models.CharField(
        max_length=10)

    history = HistoricalRecords()

    def __str__(self):
        return '{}: {}'.format(self.sender.name, self.sender_utestid_name)

    class Meta:
        app_label = 'getresults'
        db_table = 'getresults_utestidmapping'
