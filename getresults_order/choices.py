from edc_constants.constants import COMPLETE, PENDING, CANCELLED

VALUE_TYPES = (
    ('absolute', 'absolute'),
    ('calculated', 'calculated'),
)

VALUE_DATATYPES = (
    ('string', 'string'),
    ('integer', 'integer'),
    ('decimal', 'decimal'),
)

STATUS = (
    (PENDING, 'Pending'),
    (COMPLETE, 'Complete'),
    (CANCELLED, 'Cancelled'),
)
