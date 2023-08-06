from cloudcix.client import Client


class Helpdesk:
    """
    The HelpDesk application is both a ticketing system, and a returns
    management system
    """
    _application_name = 'HelpDesk'

    iris_condition = Client(
        application=_application_name,
        service_uri='IRISCondition/',
    )
    iris_defect = Client(
        application=_application_name,
        service_uri='IRISDefect/',
    )
    iris_extended_condition = Client(
        application=_application_name,
        service_uri='IRISExtendedCondition/',
    )
    iris_ntf = Client(
        application=_application_name,
        service_uri='IRISNTF/',
    )
    iris_repair = Client(
        application=_application_name,
        service_uri='IRISRepair/',
    )
    iris_section = Client(
        application=_application_name,
        service_uri='IRISSection/',
    )
    iris_symptom = Client(
        application=_application_name,
        service_uri='IRISSymptom/',
    )
    item = Client(
        application=_application_name,
        service_uri=(
            'Ticket/{idTransactionType}/{transactionSequenceNumber}/Item/'
        ),
    )
    item_history = Client(
        application=_application_name,
        service_uri=(
            'Ticket/{idTransactionType}/{transactionSequenceNumber}/Item/'
            '{idItem}/History/'
        ),
    )
    item_part_used = Client(
        application=_application_name,
        service_uri=(
            'Ticket/{idTransactionType}/{transactionSequenceNumber}/Item/'
            '{idItem}/PartUsed/'
        ),
    )
    item_status = Client(
        application=_application_name,
        service_uri='ItemStatus/',
    )
    reason_for_return = Client(
        application=_application_name,
        service_uri='ReasonForReturn/',
    )
    reason_for_return_translation = Client(
        application=_application_name,
        service_uri='ReasonForReturn/{idReasonForReturn}/Translation/',
    )
    service_centre_logic = Client(
        application=_application_name,
        service_uri='ServiceCentreLogic/',
    )
    service_centre_warrantor = Client(
        application=_application_name,
        service_uri='ServiceCentre/{idAddress}/Warrantor/',
    )
    status = Client(
        application=_application_name,
        service_uri='Status/',
    )
    ticket = Client(
        application=_application_name,
        service_uri='Ticket/{idTransactionType}/',
    )
    ticket_history = Client(
        application=_application_name,
        service_uri=(
            'Ticket/{idTransactionType}/{transactionSequenceNumber}/History/'
        ),
    )
    ticket_question = Client(
        application=_application_name,
        service_uri='TicketQuestion/',
    )
    ticket_type = Client(
        application=_application_name,
        service_uri='TicketType/',
    )
    ticket_type_question = Client(
        application=_application_name,
        service_uri='TicketType/{id}/TicketQuestion/',
    )
    warrantor_logic = Client(
        application=_application_name,
        service_uri='WarrantorLogic/',
    )
    warrantor_service_centre = Client(
        application=_application_name,
        service_uri='Warrantor/{idAddress}/ServiceCentre/',
    )
