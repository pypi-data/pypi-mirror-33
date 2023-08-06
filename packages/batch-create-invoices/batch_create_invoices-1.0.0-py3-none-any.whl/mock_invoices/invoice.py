import json
from typing import List, Dict
from datetime import datetime, timedelta

from mock_invoices.config import InvoiceTypes


class InvoiceItem:
    def __init__(self):
        self.name: str = None
        self.model: str = None
        self.unit: str = None
        self.quantity: int = None
        self.unitPrice: float = None
        self.priceAmount: float = None
        self.taxRate: float = None
        self.taxAmount: float = None


class Invoice:
    def __init__(self):
        self.invoiceCode: str = None
        self.invoiceNumber: str = None
        self.issueDate: str = None
        self.totalExTax: float = None
        self.checkCode: str = None
        self.buyerAddrPhone: str = None
        self.buyerBankAccount: str = None
        self.buyerName: str = None
        self.buyerTaxNumber: str = None
        self.region: str = None
        self.machineNumber: str = None
        self.totalTax: float = None
        self.totalInTax: float = None
        self.supplierAddrPhone: str = None
        self.supplierBankAccount: str = None
        self.supplierName: str = None
        self.supplierTaxNumber: str = None
        self.note: str = None
        self.itemList: List[InvoiceItem] = None

    def to_qr_code(self):
        date_str = self.issueDate.replace('-', '')
        return '01,04,{},{},{:.2f},{},{},7CA0'.format(self.invoiceCode, self.invoiceNumber, self.totalExTax, date_str, self.checkCode)


def get_days_of_year(date_time: datetime) -> int:
    start_date = datetime(date_time.year, 1, 1)
    delta: timedelta = date_time - start_date
    return delta.days


def get_seconds_of_year(date_time: datetime) -> int:
    start_date = datetime(date_time.year, 1, 1)
    delta: timedelta = date_time - start_date
    return delta.seconds + delta.days * 24 * 3600


def pad_left(string: str, length: int, pad: str) -> str:
    dist = length - len(string)
    return string if dist <= 0 else pad*dist + string


def _create_invoice_code(type: InvoiceTypes) -> str:
    day_of_year = str(get_days_of_year(datetime.now()))
    day_of_year = pad_left(day_of_year, 3, '0')

    year_info = datetime.now().year - 2000

    return '1234{}{}{}'.format(day_of_year, str(type.value), year_info)


def _create_invoice_num() -> str:
    seconds_of_year = get_seconds_of_year(datetime.now())
    return pad_left(str(seconds_of_year), 8, '0')


def _create_issue_date_str() -> str:
    now: datetime = datetime.now()
    return now.strftime('%Y-%m-%d')


def _create_base_mock_invoice() -> Invoice:
    vat = Invoice()
    vat.totalExTax = 100
    vat.checkCode = "12345678901234567890"
    vat.buyerAddrPhone = "买方地址电话"
    vat.buyerBankAccount = "买方开户行及账号"
    vat.buyerName = "买方名称"
    vat.region = "测试"
    vat.machineNumber = "123456789012"
    vat.totalTax = 3
    vat.totalInTax = 100
    vat.supplierAddrPhone = "销售方地址电话"
    vat.supplierBankAccount = "销售方开户行及账号"
    vat.supplierName = "销售方名称"
    vat.note = "备注"

    item = InvoiceItem()
    item.name = "名称"
    item.model = "规格"
    item.unit = "件"
    item.quantity = 1
    item.unitPrice = 100
    item.priceAmount = 100
    item.taxRate = 0.03
    item.taxAmount = 3

    vat.itemList = [item]
    return vat


def generate_mock_invoice(invoice_type: InvoiceTypes, buyer_tax_num: str, supplier_tax_num: str) -> Invoice:
    base_vat = _create_base_mock_invoice()
    base_vat.invoiceCode = _create_invoice_code(invoice_type)
    base_vat.invoiceNumber = _create_invoice_num()
    base_vat.buyerTaxNumber = buyer_tax_num
    base_vat.supplierTaxNumber = supplier_tax_num
    base_vat.issueDate = _create_issue_date_str()

    return base_vat


def generate_mock_invoice_list(invoice_type: InvoiceTypes, buyer_tax_num: str, supplier_tax_num: str, count: int) -> List[Invoice]:
    code = _create_invoice_code(invoice_type)
    num = _create_invoice_num()
    date = _create_issue_date_str()

    vat_list: List[Invoice] = []
    for offset in range(count):
        base_vat = _create_base_mock_invoice()
        base_vat.invoiceCode = code
        base_vat.invoiceNumber = str(int(num) + offset)
        base_vat.issueDate = date
        base_vat.buyerTaxNumber = buyer_tax_num
        base_vat.supplierTaxNumber = supplier_tax_num

        vat_list.append(base_vat)
    return vat_list
