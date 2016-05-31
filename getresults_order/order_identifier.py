from edc_identifier.alphanumeric_identifier import AlphanumericIdentifier


class OrderIdentifier(AlphanumericIdentifier):

    name = 'order_identifier'
    alpha_pattern = r'^[A-Z]{3}$'
    numeric_pattern = r'^[0-9]{5}$'
    seed = ['AAA', '00000']
    separator = None
