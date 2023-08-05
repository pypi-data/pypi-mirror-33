from cloudcix.client import Client


class Contacts:
    """
    The Contacts Application is a CRM application that exposes a REST API to
    manage a shared address book between Users in the same Member

    Contacts can be used as a sales and marketing tool or just as a general
    purpose address book.
    """
    _application_name = 'Contacts'

    activity = Client(
        application=_application_name,
        service_uri='ActivityType/{idActivityType}/Activity/',
    )
    activity_type = Client(
        application=_application_name,
        service_uri='ActivityType/',
    )
    campaign = Client(
        application=_application_name,
        service_uri='Campaign/',
    )
    campaign_activity = Client(
        application=_application_name,
        service_uri='Campaign/{idCampaign}/Activity/',
    )
    campaign_contact = Client(
        application=_application_name,
        service_uri='Campaign/{idCampaign}/Contact/',
    )
    contact = Client(
        application=_application_name,
        service_uri='Contact/',
    )
    group = Client(
        application=_application_name,
        service_uri='Group/',
    )
    group_contact = Client(
        application=_application_name,
        service_uri='Group/{idGroup}/Contact/',
    )
    opportunity = Client(
        application=_application_name,
        service_uri='Opportunity/',
    )
    opportunity_contact = Client(
        application=_application_name,
        service_uri='Opportunity/{idOpportunity}/Contact/',
    )
    opportunity_history = Client(
        application=_application_name,
        service_uri='Opportunity/{idOpportunity}/History/',
    )
