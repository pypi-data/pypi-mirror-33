from cloudcix.client import Client


class Repository:
    """
    The Repository Application is a software system that manages
    CloudCIX Software Projects

    Projects in the Repository are grouped by the owning Member
    """
    _application_name = 'SupportFramework'

    application = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Application/',
    )
    dto = Client(
        application=_application_name,
        service_uri='DTO/',
    )
    dto_parameter = Client(
        application=_application_name,
        service_uri='DTO/{idDTO}/Parameter/',
    )
    exception_code = Client(
        application=_application_name,
        service_uri='ExceptionCode/',
    )
    language_exception_code = Client(
        application=_application_name,
        service_uri='ExceptionCode/{exception_code}/Language/',
    )
    member = Client(
        application=_application_name,
        service_uri='Member/',
    )
    method = Client(
        application=_application_name,
        service_uri=(
            'Member/{idMember}/Application/{idApplication}/Service/'
            '{idService}/Method/'
        ),
    )
    method_parameter = Client(
        application=_application_name,
        service_uri=(
            'Member/{idMember}/Application/{idApplication}/Service/'
            '{idService}/Method/{idMethod}/Parameter/'
        ),
    )
    service = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Application/{idApplication}/Service/',
    )
