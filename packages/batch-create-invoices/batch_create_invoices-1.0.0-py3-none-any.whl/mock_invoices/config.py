from enum import Enum
from typing import List

from mock_invoices.input_util import InputOption, input_with_validate, input_with_options


class InvoiceTypes(Enum):
    NORMAL_INVOICE = '3'
    SPECIAL_INVOICE = '1'


class Config:
    def __init__(self):
        self.base_url: str = None
        self.user_name: str = None
        self.password: str = None
        self.buyer_tax_num: str = None
        self.supplier_tax_num: str = None
        self.count: int = None
        self.invoice_type: InvoiceTypes = None


def prepare_config_from_input() -> Config:
    config = Config()

    invoice_type_options: List[InputOption] = [
        InputOption('normal invoice', InvoiceTypes.NORMAL_INVOICE),
        InputOption('special invoice', InvoiceTypes.SPECIAL_INVOICE)
    ]

    config.base_url = input_with_validate('Please input host url', default_val='http://localhost:8890')
    config.user_name = input_with_validate('Please input admin user name', default_val='bwts_admin@cn.tradeshift.com')
    config.password = input_with_validate('Please input password', is_password=True)
    config.buyer_tax_num = input_with_validate('Please input buyer tax number', default_val='1234567890')
    config.supplier_tax_num = input_with_validate('Please input supplier tax number', default_val='1234567890')
    config.count = int(input_with_validate('Please input invoice count', '\d+', default_val='2'))
    config.invoice_type = input_with_options('Please choose invoice type', invoice_type_options)
    return config


def get_test_config() -> Config:
    config = Config
    config.base_url = 'https://sales-sandbox.baiwangtradeshift.com'
    config.user_name = 'bwts_admin@cn.tradeshift.com'
    config.invoice_type = InvoiceTypes.NORMAL_INVOICE
    config.buyer_tax_num = '1234567890'
    config.supplier_tax_num = '1234567890'
    config.count = 2

    return config


def test() -> None:
    config: Config = prepare_config_from_input()
    print(config)


if __name__ == '__main__':
    test()

