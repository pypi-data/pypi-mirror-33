from cloudcix.client import Client


class SCM:
    """
    SCM is an Application to manage the planning, procurement, storage,
    distribution, service and return of inventory
    """
    _application_name = 'SCM'

    bin = Client(
        application=_application_name,
        service_uri='Bin/',
    )
    bin_sku = Client(
        application=_application_name,
        service_uri='Bin/{id}/SKU/',
    )
    brand = Client(
        application=_application_name,
        service_uri='Brand/',
    )
    # idSKUComponent should be passed as pk to resource methods
    critical_bom = Client(
        application=_application_name,
        service_uri='SKU/{idSKU}/BOM/',
    )
    # CriticalBOM for member returns all BOM records for the idMember
    # doing the request
    critical_bom_for_member = Client(
        application=_application_name,
        service_uri='SKU/BOM/',
    )
    manufactured_item = Client(
        application=_application_name,
        service_uri='ManufacturedItem/',
    )
    return_question = Client(
        application=_application_name,
        service_uri='ReturnQuestion/',
    )
    return_question_field_type = Client(
        application=_application_name,
        service_uri='ReturnQuestionFieldType/',
    )
    service_group = Client(
        application=_application_name,
        service_uri='ServiceGroup/',
    )
    sku = Client(
        application=_application_name,
        service_uri='SKU/',
    )
    sku_category = Client(
        application=_application_name,
        service_uri='SKUCategory/',
    )
    sku_category_return_question = Client(
        application=_application_name,
        service_uri='SKUCategory/{idSKUCategory}/ReturnQuestion/',
    )
    sku_stock = Client(
        application=_application_name,
        service_uri='SKU/{idSKU}/Stock/',
    )
    sku_stock_adjustment = Client(
        application=_application_name,
        service_uri='SKUStockAdjustment/',
    )
    sku_value = Client(
        application=_application_name,
        service_uri='SKU/{idSKU}/Value/',
    )
