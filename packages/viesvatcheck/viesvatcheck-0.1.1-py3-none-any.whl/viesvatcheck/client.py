from typing import Tuple, Optional, Dict

import zeep
from zeep.exceptions import Fault
from zeep.helpers import serialize_object
from .exceptions import EXCEPTION_MAP, OtherError, NotEUMember
from .countries import is_eu_member

PROD_WSDL = "http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl"
TEST_WSDL = "http://ec.europa.eu/taxation_customs/vies/checkVatTestService.wsdl"

Response = Tuple[bool, Optional[Dict]]


class Client(object):
    def __init__(self, wsdl: str = PROD_WSDL) -> None:
        self.zeep = zeep.CachingClient(wsdl=wsdl)

    def check(self, country_code: str, vat_number: str) -> Response:
        country_code = country_code.upper()
        if not is_eu_member(country_code):
            raise NotEUMember

        """
        http://publications.europa.eu/code/pdf/370000en.htm
        The abbreviations to use are the ISO codes, except for Greece and the United Kingdom,
        for which EL and UK are recommended (instead of GR and GB).
        The former abbreviations were generally taken from the international code for automobiles and were used
        until the end of 2002.

        United Kingodm is fine but we have to remap Greece???
        """
        if country_code == 'GR':
            country_code = 'EL'

        try:
            response = self.zeep.service.checkVat(
                countryCode=country_code, vatNumber=vat_number)
            return response.valid, serialize_object(response, dict)
        except Fault as error:
            try:
                raise EXCEPTION_MAP[error.message]
            except KeyError:
                raise OtherError
