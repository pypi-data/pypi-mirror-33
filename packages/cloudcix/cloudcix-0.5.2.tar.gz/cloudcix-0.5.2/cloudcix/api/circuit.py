from cloudcix.client import Client


class Circuit:
    """
    The Circuit Application allows for the management of circuits and devices.
    """
    _application_name = 'Circuit'

    circuit = Client(
        application=_application_name,
        service_uri='Circuit/',
    )
    circuit_class = Client(
        application=_application_name,
        service_uri='CircuitClass/',
    )
    property_type = Client(
        application=_application_name,
        service_uri='PropertyType/',
    )
