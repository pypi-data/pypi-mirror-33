"""Simple client for Moneyou accounts."""
from typing import List, Dict, Iterable
from types import FunctionType
import requests
from lxml import etree
from io import StringIO
import logging

SERVER_URL = 'https://www.moneyou.de/'
LOGIN_URL = SERVER_URL + 'persoenlicheseite/login'
OVERVIEW_URL = SERVER_URL + 'PersoenlicheSeite/Uebersicht'
LOGOUT_URL = SERVER_URL + 'personalpage/api/security/logout'
AMOUNT_SEARCH_PATH = 'div[{}]/div[@class="mymoney"]/span[@class="myammount"]'

_LOGGER = logging.getLogger(__name__)


class Account(object):
    """Bank account."""

    def __init__(self, html: etree):
        """Constructor."""
        self.name = None           # type: str
        self.iban = None           # type: str
        self.balance = None        # type: float
        self.interest_sum = None   # type: float
        self.interest_rate = None  # type: float
        self.currency = None       # type: str
        self._listeners = []       # type: List[FunctionType]
        self._parse_html(html)

    def _parse_html(self, html: etree) -> None:
        """Parse the html code returned from server."""
        self.name = html.xpath('//div[@class="mytitle h4"]')[0].text
        self.iban = html.xpath('//div[@class="mysubtitle h4"]')[0].text

        panel = html.xpath('//div[@class="myPanelData"]')[0]
        self.currency = panel.xpath('//span[@class="mycurr"]')[0].text
        self.balance = self._parse_float(panel.xpath(
            AMOUNT_SEARCH_PATH.format(1))[0].text)
        self.interest_sum = self._parse_float(panel.xpath(
            AMOUNT_SEARCH_PATH.format(2))[0].text)
        self.interest_rate = self._parse_float(panel.xpath(
            AMOUNT_SEARCH_PATH.format(3))[0].text)
        self._notify_listeners()

    @staticmethod
    def _parse_float(text: str) -> float:
        """Parse a float in german notation."""
        text = text.replace('.', '').replace(',', '.')
        return float(text)

    def update_from_account(self, other: "Account") -> None:
        """Update the data of an account from another account."""
        if self.iban != other.iban:
            raise Exception("cannot update from account with different IBAN")

        self.name = other.name
        self.balance = other.balance
        self.interest_rate = other.interest_rate
        self.interest_sum = other.interest_sum
        self.currency = other.currency
        self._notify_listeners()

    def _notify_listeners(self):
        """Notify listeners about an update."""
        for listener in self._listeners:
            listener()

    def add_listener(self, callback: FunctionType):
        """Add a listener for changes to the data."""
        self._listeners.append(callback)


class MonpYou(object):
    """Client to interact with Moneyou bank accounts."""

    def __init__(self, username: str, password: str):
        """Constructor."""
        if not (username and password):
            raise Exception("username and password must not be None!")
        self._username = username  # type: str
        self._password = password  # type: str
        self._session = None        # type: requests.Session
        self._accounts = dict()  # type: Dict[str, Account]

    def __del__(self):
        """Destructor."""
        self.logout()

    @property
    def session(self) -> requests.Session:
        """The the current requests session.

        Creates a new session if it does not exist.
        """
        if not self._session:
            self._start_new_session()
        return self._session

    def _start_new_session(self) -> None:
        """Login to server, get the cookie."""
        _LOGGER.info('Logging in...')
        self._session = requests.Session()
        params = {
            "fakepasswordremembered": "",
            "UserId": self._username,
            "Password": self._password,
            "RememberMe": False,
        }
        response = self.session.post(LOGIN_URL, params=params)
        if response.status_code not in [200, 302]:
            raise Exception('Received error {} from server: \n{}'.format(response.status_code, response.text))

    def update_accounts(self) -> None:
        """Update list of accounts."""
        _LOGGER.info('Getting account data...')
        response = self.session.get(OVERVIEW_URL)
        if response.status_code != 200:
            raise Exception('Received error {} from server: \n{}'.format(response.status_code, response.text))
        accounts = self._parse_account_html(response.text)
        for account in accounts:
            if account.iban in self._accounts:
                self._accounts[account.iban].update_from_account(account)
            else:
                self._accounts[account.iban] = account

    @property
    def accounts(self) -> Iterable[Account]:
        """Get list of accounts."""
        return self._accounts.values()

    def get_account(self, iban: str) -> Account:
        """Get account for a give IBAN."""
        return self._accounts.get(iban)

    @staticmethod
    def _parse_account_html(html: str) -> List[Account]:
        """Parse the account html tree."""
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html), parser)
        accounts = tree.xpath('//div[@id="savingsAccountBlock0"]')
        return [Account(a) for a in accounts]

    def logout(self) -> None:
        """Logout from server."""
        _LOGGER.info('Logging out...')
        if not self.session:
            return

        response = self.session.get(LOGOUT_URL)
        if response.status_code != 200:
            raise Exception('Received error {} from server: \n{}'.format(response.status_code, response.text))
        self._session = None
