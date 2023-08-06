from cloudcix.client import Client


class Documentation:
    """
    The Documentation Application reads the Repository database and
    generates responses to generate documentation via Swagger
    """
    _application_name = 'Documentation'

    application = Client(
        application=_application_name,
        service_uri='Application/',
    )
