from cloudcix.client import Client


class Security:
    """
    Security is a service whose main function is to manage visitors and staff
    entering and exiting a building.

    Users will be able to see where they went and when.

    Administrators will be able to see where their Users went and when, as well
    as visitors to their own Addresses
    """
    _application_name = 'Security'

    security_event = Client(
        application=_application_name,
        service_uri='SecurityEvent/',
    )
    security_event_logout = Client(
        application=_application_name,
        service_uri='SecurityEvent/{idUser}/Logout/',
    )
