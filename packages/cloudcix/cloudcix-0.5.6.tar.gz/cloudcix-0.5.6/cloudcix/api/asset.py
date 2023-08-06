from cloudcix.client import Client


class Asset:
    """
    The Asset Application enables the management of Assets owned by a Member.

    Examples of Assets are buildings, machinery, furniture, vehicles, etc.
    """
    _application_name = 'Asset'

    asset = Client(
        application=_application_name,
        service_uri='Asset/',
    )
    asset_transaction = Client(
        application=_application_name,
        service_uri='Asset/{idAsset}/Transaction/',
    )
    depreciation_type = Client(
        application=_application_name,
        service_uri='DepreciationType/',
    )
    off_rent = Client(
        application=_application_name,
        service_uri='OffRent/',
    )
    off_test = Client(
        application=_application_name,
        service_uri='OffTest/',
    )
    rent = Client(
        application=_application_name,
        service_uri='Rent/',
    )
