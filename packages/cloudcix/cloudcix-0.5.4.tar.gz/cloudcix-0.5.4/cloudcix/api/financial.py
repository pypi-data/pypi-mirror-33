from cloudcix.client import Client


class Financial:
    """
    The Financial Application exposes a suite of services that together
    implement a full accounting system based on double entry bookkeeping
    """
    _application_name = 'Financial'

    account_purchase_adjustment = Client(
        application=_application_name,
        service_uri='AccountPurchaseAdjustment/',
    )
    account_purchase_adjustment_contra = Client(
        application=_application_name,
        service_uri='AccountPurchaseAdjustment/{idAddress}/Contra/',
    )
    account_purchase_debit_note = Client(
        application=_application_name,
        service_uri='AccountPurchaseDebitNote/',
    )
    account_purchase_debit_note_contra = Client(
        application=_application_name,
        service_uri='AccountPurchaseDebitNote/{idAddress}/Contra/',
    )
    account_purchase_invoice = Client(
        application=_application_name,
        service_uri='AccountPurchaseInvoice/',
    )
    account_purchase_invoice_contra = Client(
        application=_application_name,
        service_uri='AccountPurchaseInvoice/{idAddress}/Contra/',
    )
    account_purchase_payment = Client(
        application=_application_name,
        service_uri='AccountPurchasePayment/',
    )
    account_purchase_payment_contra = Client(
        application=_application_name,
        service_uri='AccountPurchasePayment/{idAddress}/Contra/',
    )
    account_sale_adjustment = Client(
        application=_application_name,
        service_uri='AccountSaleAdjustment/',
    )
    account_sale_adjustment_contra = Client(
        application=_application_name,
        service_uri='AccountSaleAdjustment/{idAddress}/Contra/',
    )
    account_sale_credit_note = Client(
        application=_application_name,
        service_uri='AccountSaleCreditNote/',
    )
    account_sale_credit_note_contra = Client(
        application=_application_name,
        service_uri='AccountSaleCreditNote/{idAddress}/Contra/',
    )
    account_sale_invoice = Client(
        application=_application_name,
        service_uri='AccountSaleInvoice/',
    )
    account_sale_invoice_contra = Client(
        application=_application_name,
        service_uri='AccountSaleInvoice/{idAddress}/Contra/',
    )
    account_sale_payment = Client(
        application=_application_name,
        service_uri='AccountSalePayment/',
    )
    account_sale_payment_contra = Client(
        application=_application_name,
        service_uri='AccountSalePayment/{idAddress}/Contra/',
    )
    allocation = Client(
        application=_application_name,
        service_uri='Allocation/',
    )
    business_logic = Client(
        application=_application_name,
        service_uri='BusinessLogic/',
    )
    cash_purchase_debit_note = Client(
        application=_application_name,
        service_uri='CashPurchaseDebitNote/',
    )
    cash_purchase_debit_note_contra = Client(
        application=_application_name,
        service_uri='CashPurchaseDebitNote/{idAddress}/Contra/',
    )
    cash_purchase_invoice = Client(
        application=_application_name,
        service_uri='CashPurchaseInvoice/',
    )
    cash_purchase_invoice_contra = Client(
        application=_application_name,
        service_uri='CashPurchaseInvoice/{idAddress}/Contra/',
    )
    cash_sale_credit_note = Client(
        application=_application_name,
        service_uri='CashSaleCreditNote/',
    )
    cash_sale_credit_note_contra = Client(
        application=_application_name,
        service_uri='CashSaleCreditNote/{idAddress}/Contra/',
    )
    cash_sale_invoice = Client(
        application=_application_name,
        service_uri='CashSaleInvoice/',
    )
    cash_sale_invoice_contra = Client(
        application=_application_name,
        service_uri='CashSaleInvoice/{idAddress}/Contra/',
    )
    creditor_account_history = Client(
        application=_application_name,
        service_uri='CreditorAccount/{id}/History/',
    )
    creditor_account_statement = Client(
        application=_application_name,
        service_uri='CreditorAccount/{id}/Statement/',
    )
    creditor_account_statement_log = Client(
        application=_application_name,
        service_uri='CreditorAccount/{id}/Statement/',
    )
    creditor_ledger = Client(
        application=_application_name,
        service_uri='CreditorLedger/',
    )
    creditor_ledger_aged = Client(
        application=_application_name,
        service_uri='CreditorLedger/Aged/',
    )
    creditor_ledger_transaction = Client(
        application=_application_name,
        service_uri='CreditorLedger/Transaction/',
    )
    creditor_ledger_transaction_contra = Client(
        application=_application_name,
        service_uri='CreditorLedger/ContraTransaction/',
    )
    debtor_account_history = Client(
        application=_application_name,
        service_uri='DebtorAccount/{id}/History/',
    )
    debtor_account_statement = Client(
        application=_application_name,
        service_uri='DebtorAccount/{id}/Statement/',
    )
    debtor_account_statement_log = Client(
        application=_application_name,
        service_uri='DebtorAccount/StatementLog/',
    )
    debtor_ledger = Client(
        application=_application_name,
        service_uri='DebtorLedger/',
    )
    debtor_ledger_aged = Client(
        application=_application_name,
        service_uri='DebtorLedger/Aged/',
    )
    debtor_ledger_transaction = Client(
        application=_application_name,
        service_uri='DebtorLedger/Transaction/',
    )
    debtor_ledger_transaction_contra = Client(
        application=_application_name,
        service_uri='DebtorLedger/ContraTransaction/',
    )
    journal_entry = Client(
        application=_application_name,
        service_uri='JournalEntry/',
    )
    nominal_account = Client(
        application=_application_name,
        service_uri='NominalAccount/',
    )
    nominal_account_history = Client(
        application=_application_name,
        service_uri='NominalAccount/{id}/History/',
    )
    nominal_account_type = Client(
        application=_application_name,
        service_uri='NominalAccountType/',
    )
    nominal_contra = Client(
        application=_application_name,
        service_uri='NominalContra/',
    )
    nominal_ledger_balance_sheet = Client(
        application=_application_name,
        service_uri='NominalLedger/BalanceSheet/',
    )
    nominal_ledger_profit_loss = Client(
        application=_application_name,
        service_uri='NominalLedger/ProfitLoss/',
    )
    nominal_ledger_purchases_by_country = Client(
        application=_application_name,
        service_uri='NominalLedger/PurchasesByCountry/',
    )
    nominal_ledger_sales_by_country = Client(
        application=_application_name,
        service_uri='NominalLedger/SalesByCountry/',
    )
    nominal_ledger_trial_balance = Client(
        application=_application_name,
        service_uri='NominalLedger/TrialBalance/',
    )
    nominal_ledger_VIES_purchases = Client(
        application=_application_name,
        service_uri='NominalLedger/VIESPurchases/',
    )
    nominal_ledger_VIES_sales = Client(
        application=_application_name,
        service_uri='NominalLedger/VIESSales/',
    )
    payment_method = Client(
        application=_application_name,
        service_uri='PaymentMethod/',
    )
    period_end = Client(
        application=_application_name,
        service_uri='PeriodEnd/',
    )
    tax_rate = Client(
        application=_application_name,
        service_uri='TaxRate/',
    )
    year_end = Client(
        application=_application_name,
        service_uri='YearEnd/',
    )
