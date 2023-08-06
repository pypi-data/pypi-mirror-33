from cloudcix.client import Client


class Reporting:
    """
    The Reporting Engine is a powerful service allowing users to generate HTML
    and PDF documents from templates
    """
    _application_name = 'Reporting'

    export = Client(
        application=_application_name,
        service_uri='Export/',
    )
    package = Client(
        application=_application_name,
        service_uri='Package/',
    )
    report = Client(
        application=_application_name,
        service_uri='Report/',
    )
    report_template = Client(
        application=_application_name,
        service_uri='ReportTemplate/',
    )
