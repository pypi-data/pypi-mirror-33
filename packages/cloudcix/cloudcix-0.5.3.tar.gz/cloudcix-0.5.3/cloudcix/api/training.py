from cloudcix.client import Client


class Training:
    """
    The Training Application exposes a REST API capable of managing Training
    records
    """
    _application_name = 'Training'

    cls = Client(
        application=_application_name,
        service_uri='Class/',
    )
    student = Client(
        application=_application_name,
        service_uri='Student/',
    )
    syllabus = Client(
        application=_application_name,
        service_uri='Syllabus/',
    )
