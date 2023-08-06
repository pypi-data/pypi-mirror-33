from cloudcix.client import Client


class Membership:
    """
    Membership is a CloudCIX Application that exposes a REST API capable of
    managing CloudCIX Members and relationships between those Members
    """
    _application_name = 'Membership'
    address = Client(
        application=_application_name,
        service_uri='Address/',
    )
    address_link = Client(
        application=_application_name,
        service_uri='Address/{idAddress}/Link/',
    )
    country = Client(
        application=_application_name,
        service_uri='Country/',
    )
    currency = Client(
        application=_application_name,
        service_uri='Currency/',
    )
    department = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Department/',
    )
    language = Client(
        application=_application_name,
        service_uri='Language/',
    )
    member = Client(
        application=_application_name,
        service_uri='Member/',
    )
    member_link = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Link/',
    )
    notification = Client(
        application=_application_name,
        service_uri='Address/{idAddress}/Notification/',
    )
    profile = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Profile/',
    )
    subdivision = Client(
        application=_application_name,
        service_uri='Country/{idCountry}/Subdivision/',
    )
    team = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Team/',
    )
    territory = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Territory/',
    )
    timezone = Client(
        application=_application_name,
        service_uri='Timezone/',
    )
    transaction_type = Client(
        application=_application_name,
        service_uri='TransactionType/',
    )
    user = Client(
        application=_application_name,
        service_uri='User/',
    )
