"""Encapsulation of data access for the Tink client."""

import Categorisation.Common.util as util
import Categorisation.Common.config as cfg

import sys
import collections
import logging

import abc  # https://pymotw.com/3/abc/


class TinkDAO:

    """
    Class that provides data access for the Tink client application.

    The Data Access Object is the single point of contact for any interaction with data sources
    like files, databases or similar.

    """

    fieldnames_user = ('userExternalId', 'label', 'market', 'locale')

    fieldnames_acc = ('userExternalId', 'externalId', 'availableCredit', 'balance', 'name',
                      'type', 'flags', 'number', 'reservedAmount')

    fieldnames_trx = ('amount', 'date', 'description', 'externalId', 'payload', 'pending',
                      'tinkId', 'type', 'n26cat', 'currency')

    def __init__(self):
        """ Initialization. """
        # Data sources
        self.user_src = 'unbound'
        self.acc_src = 'unbound'
        self.trx_src = 'unbound'

        # Data collections
        self.users = collections.OrderedDict()
        self.accounts = collections.OrderedDict()
        self.transactions = collections.OrderedDict()

        # File handler utility
        self.file_handler = util.FileHandler()


    def bind_data_source(self, src_type, locator):
        """
        Binding between a data source and a locator.

        :param src_type: Instance of class config.TinkEntityType.UserEntity
        :param locator: A locator to the required data like e.g. a filename or a filepath
        :return: void
        """
        if src_type == cfg.TinkEntityType.UserEntity:
            self.user_src = locator
        elif src_type == cfg.TinkEntityType.AccountEntity:
            self.acc_src = locator
        elif src_type == cfg.TinkEntityType.TransactionEntity:
            self.trx_src = locator

    def read_users(self, force_read=True):
        """
        Read user data from a data access object (DAO).

        :param force_read: force to read again even if there is already data
        :return: user data as an instance of <class 'list'>: [OrderedDict()]
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        if not self.users or force_read is True:
            data = self.file_handler.read_csv_file(filename=self.user_src, fieldnames=TinkDAO.fieldnames_user)

            self.users = data  # Returns a List<OrderedDict>

        return self.users

    def read_accounts(self, force_read=True):
        """
        Read account data from a data access object (DAO).

        :param force_read: force to read again even if there is already data
        :return: account data as an instance of <class 'list'>: [OrderedDict()]
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        if not self.accounts or force_read is True:
            data = self.file_handler.read_csv_file(filename=self.acc_src, fieldnames=TinkDAO.fieldnames_acc)

            self.accounts = data  # Returns a List<OrderedDict>

        return self.accounts

    def read_transactions(self, force_read=True):
        """
        Read transaction data from a data access object (DAO).

        :param force_read: force to read again even if there is already data
        :return: transaction data as an instance of <class 'list'>: [OrderedDict()]
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        if not self.transactions or force_read is True:
            data = self.file_handler.read_csv_file(filename=self.trx_src, fieldnames=TinkDAO.fieldnames_trx)

            self.transactions = data  # Returns a List<OrderedDict>

        return self.transactions


class TinkEntity:

    """
    Generic object representation of a Tink data structure.

    This class can be used to inherit from in sub-classes.
    """

    def __init__(self, fields: tuple, data: collections.OrderedDict()):
        """
        Initialization.

        :param data: the raw data as an OrderedDict.
        """
        self.data: collections.OrderedDict() = data

        # Check that all expected fields are provided
        for f in fields:
            if f not in data:
                msg = 'Field {f} expected but not found in data {d}'.format(f=f, d=data)
                raise AttributeError(msg)


class TinkEntityList(metaclass=abc.ABCMeta):

    """
    Generic object representation of a Tink data structure list.

    This class can be used to inherit from in sub-classes.
    """

    def __init__(self, data: list(collections.OrderedDict())):
        """
        Initialization.

        :param data: the raw data as list of OrderedDict.
        """
        self.data: list(collections.OrderedDict()) = data

    @abc.abstractmethod
    def get_data(self, ext_user_id: str):
        raise NotImplementedError()


class TinkAccount(TinkEntity):

    """
    Object representation of a Tink account data structure.

    This object can be used in order to create lists of accounts.
    """

    def __init__(self, data: collections.OrderedDict()):
        """
        Initialization
        :param data: the raw data as a list(OrderedDict).
        """
        super().__init__(data)


@TinkEntityList.register
class TinkAccountList(TinkEntityList):
    """
    Object representation of a Tink account data structure.

    This object can be used in order to create lists of accounts.
    """
    def __init__(self, data: collections.OrderedDict()):
        """
        Initialization
        :param data: the raw data as a list(OrderedDict).
        """
        self.data = data

    def get_data(self, ext_user_id):
        """
        This method returns a list that contains all the account data that belongs to a
        certain user.

        :param ext_user_id: external user reference (this is NOT the Tink internal id)

        :return: A list(OrderedDict) of accounts (account data) that belong to the user.
        """

        lst = list()
        for e in self.data:
            key = 'userExternalId'
            if key in e:
                lst.append(e)

