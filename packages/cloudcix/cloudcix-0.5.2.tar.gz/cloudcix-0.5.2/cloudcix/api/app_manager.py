from cloudcix.client import Client


class AppManager:
    """
    The App Manager Application is a software system that manages CloudCIX Apps

    It allows Users to select and use apps, and allows Administrators to select
    which apps to deploy and give permissions to other Users.
    """
    _application_name = 'AppManager'

    app = Client(
        application=_application_name,
        service_uri='App/',
    )
    app_member = Client(
        application=_application_name,
        service_uri='App/{idApp}/Member/',
    )
    app_menu = Client(
        application=_application_name,
        service_uri='App/{idApp}/MenuItem/',
    )
    menu_item_user = Client(
        application=_application_name,
        service_uri='MenuItem/User/{idUser}/',
    )
