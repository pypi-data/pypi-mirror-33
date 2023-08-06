from typing import Dict, List
from datetime import datetime, timedelta

import json
import requests
from mock_invoices.config import Config, get_test_config, InvoiceTypes, prepare_config_from_input
from mock_invoices.invoice import InvoiceItem, Invoice, generate_mock_invoice_list


class AuthenticationError(Exception):
    pass


class BatchCreateInvoices:
    def __init__(self):
        self.config: Config = None
        self.is_login: bool = False
        self.session: requests.Session = None

    def set_config(self, config: Config):
        self.config = config

    def login(self):
        self.session = requests.session()
        url = self.config.base_url + '/login'
        body = {'username': self.config.user_name, 'password': self.config.password}
        login_res = login_res = self.session.post(url, body)
        if login_res.status_code != 200:
            raise AuthenticationError("User name or password error")
        self.is_login = True

    def _generate_mock_invoice(self):
        list_url = self.config.base_url + '/services/ultimateinvoicelookup/mock/invoice'
        list_req = self.session.get(list_url)
        print(list_req.json())

    def _upload_invoices(self) -> List[Invoice]:
        invoice_list: List[Invoice] = generate_mock_invoice_list(self.config.invoice_type, self.config.buyer_tax_num,
                                                                 self.config.supplier_tax_num, self.config.count)
        uploaded_list: List[Invoice] = []
        for invoice in invoice_list:
            json_str = json.dumps(invoice, default=lambda o: o.__dict__)
            json_obj = json.loads(json_str)
            url = self.config.base_url + '/services/ultimateinvoicelookup/mock/invoice'
            try:
                req = self.session.post(url, json=json_obj)
                if 400 <= req.status_code < 500:
                    raise Exception('Request Error! Status code {}, detail {}'.format(req.status_code, req.content))
                if req.status_code >= 500:
                    err = req.json()
                    if err['code'] == 'MOCK_INVOICE_ADD_FAILED':
                        print('Failed to insert invoice! Reason: {:s}, invoice: {:s}'.format(err['message'], invoice))
                    else:
                        raise Exception('Server Error! Status code {}, detail {}'.format(req.status_code, req.content))

                uploaded_list.append(invoice)
            except IOError:
                print('Connection error')
            except AuthenticationError:
                print('Login needed')
                return uploaded_list
            except Exception as err:
                print(err)
                return uploaded_list
        return uploaded_list

    @staticmethod
    def print_qr_codes(qr_list: List[str]):
        for qr in qr_list:
            print(qr)

    def run(self):
        qr_list: List[str] = None
        config: Config = prepare_config_from_input()
        self.set_config(config)
        try:
            self.login()
            self.is_login = True
            upload_invoices: List[Invoice] = self._upload_invoices()
            qr_list = list(map(lambda vat: vat.to_qr_code(), upload_invoices))
            self.print_qr_codes(qr_list)
        except AuthenticationError as err:
            print(err)
            self.session.close()
            return
        except IOError:
            print('Can not connect to server')
            self.session.close()
            return


def test():
    cls = BatchCreateInvoices()
    config = get_test_config()
    cls.set_config(config)
    cls.run()


if __name__ == '__main__':
    test()