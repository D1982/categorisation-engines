"""Encapsulation of data access for the Tink client."""

import Categorisation.Common.util as util
import Categorisation.Common.config as cfg
import Categorisation.Common.exceptions as ex

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

    # Standard fields for entity User

    fields_user_input = ('userExternalId', 'label', 'market', 'locale')

    fields_user_api = ('userExternalId', 'label', 'market', 'locale')

    # Standard fields for entity Account

    fields_acc_input = ('userExternalId', 'externalId', 'availableCredit', 'balance',
                        'name', 'type', 'flags', 'number', 'reservedAmount')

    fields_acc_map = ('flags', 'closed', 'payload')

    fields_acc_api = ('externalId', 'availableCredit', 'balance', 'closed',
                      'name', 'type', 'flags', 'number', 'reservedAmount', 'payload')

    # Standard fields for entity Transaction

    fields_trx_input = ('amount', 'date', 'description', 'externalId', 'payload',
                        'pending', 'tinkId', 'type', 'n26cat', 'currency')

    fields_trx_map = ()

    fields_trx = fields_trx_input

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
            data = self.file_handler.read_csv_file(filename=self.user_src, fieldnames=TinkDAO.fields_user_input)

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
            data = self.file_handler.read_csv_file(filename=self.acc_src, fieldnames=TinkDAO.fields_acc_input)

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
            data = self.file_handler.read_csv_file(filename=self.trx_src, fieldnames=TinkDAO.fields_trx_input)

            self.transactions = data  # Returns a List<OrderedDict>

        return self.transactions


class TinkEntity(metaclass=abc.ABCMeta):

    """
    Generic object representation of a Tink data structure.

    This class can be used to inherit from in sub-classes.
    """

    def __init__(self, fields: tuple, data: collections.OrderedDict = None):
        """
        Initialization.
        :param fields: The expected fields provided as keys in data.
        :param data: the raw data as an OrderedDict.
        """
        if not isinstance(data, collections.OrderedDict):
            raise ex.ParameterError(f'Expected a parameter of type OrderedDict')
        else:
            self.data = data

        # Make sure that all expected fields are provided within data
        for f in fields:
            if f not in data:
                msg = 'Field {f} expected but not found in data {d}'.format(f=f, d=data)
                raise AttributeError(msg)

    @abc.abstractmethod
    def get_data(self):
        """
        This method returns the data belonging to a single TinkEntity instance.

        :return: the data of a single entity wrapped within an instance of this class.
        """
        raise NotImplementedError()


class TinkEntityList(metaclass=abc.ABCMeta):

    """
    Generic object representation of a Tink data structure list.

    This class can be used to inherit from in sub-classes.
    """

    def __init__(self, lst: list = list()):
        """
        Converts a standard list into a list of TinkEntity object references that
        can be used as an input for the constructor of the class TinkEntityList.

        :param lst:  A list of TinkEntity object references or any other typing.
        :return: a list of TinkEntity object references wrapping the input data.
        :raise: AttributeError if one of the elements in parameter lst does not conform
        with the the field requirements when trying to create an entity object from it.
        :raise: NotImplementedError if the type of this instance does not support the
        creation of an entity object from it - see TinkEntity.__init__()
        """
        self.entities = list()

        if len(lst) == 0:
            raise AttributeError(f'Expected a list containing elements in parameter lst')

        for e in lst:
            if isinstance(self, TinkAccountList):
                if isinstance(e, TinkAccount):
                    self.entities.append(e)
                else:
                    try:
                        entity = TinkAccount(fields=TinkDAO.fields_acc_input,
                                             data=e)
                        self.entities.append(entity)
                    except AttributeError as ex_att:
                        raise ex_att
                # TODO: Add transaction scope here
            else:
                raise NotImplementedError(f"Type of {str(type(self))} not supported")

    @abc.abstractmethod
    def get_data(self, ext_user_id: str):
        """
        This method returns the contained TinkEntity data.

        :param ext_user_id: external user reference (this is NOT the Tink internal id).
        If provided then the data returned will be restricted to the records that belong
        to the user ext_user_id.

        :return: the wrapped data as a standard list[OrderedDict]
        this class.

        :raise NotImplementedError if this method was not implemented in a sub-class.
        """
        raise NotImplementedError()


@TinkEntity.register
class TinkAccount(TinkEntity):

    """
    An object representation of a Tink account data structure.
    This object can be used in order to create lists of accounts.
    """

    def __init__(self, fields: tuple, data: collections.OrderedDict = None):
        """
        Initialization
        :param fields: The expected fields provided as keys in data.
        :param data: the raw data as an OrderedDict.
        """

        super().__init__(fields, data)

    def get_data(self):
        """
        This method returns the data belonging to a single TinkEntity instance.

        :return: the data of a single entity wrapped within an instance of this class.
        """
        data = collections.OrderedDict()

        fields_unmapped_str = ''

        for field in TinkDAO.fields_acc_input:

            if field in TinkDAO.fields_acc_api:
                # Field to be provided to the API as is
                data[field] = self.data[field]
            elif field in TinkDAO.fields_acc_map:
                # Field to be mapped against the API
                if field == 'flags':
                    # field "flags" is specified as an array
                    data[field] = (data[field])
                elif field == 'closed':
                    data[field] = ''
                elif field == 'payload':
                    data[field] = ''
                else:
                    if fields_unmapped_str == '':
                        fields_unmapped_str += f'{field}'
                    else:
                        fields_unmapped_str += f', {field}'

        if fields_unmapped_str != '':
            raise RuntimeError(f'Unmapped fields in: {str(type(self))} {fields_unmapped_str}')

        return data


@TinkEntityList.register
class TinkAccountList(TinkEntityList):
    """
    Object representation of a Tink account data structure.

    This object can be used in order to create lists of accounts.
    """

    def __init__(self, lst: list = None):
        """
        Initialization.

        :param lst: a list of TinkEntity object references.
        """
        super().__init__(lst)

    def get_data(self, ext_user_id: str = None):
        """
        This method returns the contained TinkEntity data.

        :param ext_user_id: external user reference (this is NOT the Tink internal id).
        If provided then the data returned will be restricted to the records that belong
        to the user ext_user_id.

        :return: the wrapped data as a standard list[OrderedDict]
        this class.
        """
        lst = list()

        if ext_user_id:
            # Add only data to the result list if it belongs to the user ext_user_id
            for entity in self.entities:
                if entity.data['userExternalId'] == ext_user_id:
                    lst.append(entity.get_data())
        else:
            # Add all the data to the result list
            lst = self.entities

        return lst

