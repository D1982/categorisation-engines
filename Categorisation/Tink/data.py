"""Encapsulation of data access for the Tink client."""

import Categorisation.Common.util as util
import Categorisation.Common.config as cfg
import Categorisation.Common.exceptions as ex

import Categorisation.Tink.api as api


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
        # Input data collections
        self._users_input = collections.OrderedDict()
        self._accounts_input = collections.OrderedDict()
        self._transactions_input = collections.OrderedDict()

        # Data collections
        self._users: TinkEntityList = None
        self._accounts: TinkEntityList = None
        self._transactions: TinkEntityList = None

        # Instance of a file handler utility
        self.file_handler = util.FileHandler()

    def get_input_data(self, entity_type: cfg.EntityType,
                       source_type: cfg.InputSourceType,
                       force_read=False):
        """
        Read user data from a data access object (DAO).
        :param entity_type: The entity type of interest.
        :param source_type: Input source type (kind of input data for the DAO).
        :param force_read: Force to read again even if there is already data.
        :return: The user data as an instance of <class 'list'>: [OrderedDict()]
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)
        logging.info(f'source_type: {source_type.value}')

        if source_type != cfg.InputSourceType.File:
            msg = f'Input source types other than {cfg.InputSourceType.File} are not yet supported'
            raise NotImplementedError(msg)

        if entity_type == cfg.EntityType.Log:
            locator = cfg.TINK_LOGFILE
        elif entity_type == cfg.EntityType.User:
            data = self._users_input
            locator = cfg.TinkConfig.get_instance().user_source
            fields = TinkDAO.fields_user_input
        elif entity_type == cfg.EntityType.Account:
            data = self._accounts_input
            locator = cfg.TinkConfig.get_instance().account_source
            fields = TinkDAO.fields_acc_input
        elif entity_type == cfg.EntityType.Transaction:
            data = self._transactions_input
            locator = cfg.TinkConfig.get_instance().transaction_source
            fields = TinkDAO.fields_trx_input

        if not data or force_read is True:
            try:
                data = self.file_handler.read_csv_file(filename=locator, fieldnames=fields)
            except Exception as e:
                raise e

        return data

    @property
    def users(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        pass

    @users.setter
    def users(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        pass

    @property
    def accounts(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        pass

    @accounts.setter
    def accounts(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        pass

    @property
    def transactions(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        pass

    @transactions.setter
    def transactions(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        pass


class TinkEntity:

    """
    Object representation of a Tink entity data structure.
    """

    @staticmethod
    def create_from_http_response(entity_type: cfg.EntityType, response):
        """
        :param entity_type: The entity type - a value of the Enum config.EntityType.
        :param response: A response of a supported sub-type of TinkAPIResponse containing the data.
        :return: An instance of the class TinkEntity.
        """
        if entity_type == cfg.EntityType.User:
            return TinkEntity(cfg.EntityType.User, response)

    def __init__(self, entity_type: cfg.EntityType,
                       data: collections.OrderedDict = None):
        """
        Initialization.
        :param entity_type: The entity type - a value of the Enum config.EntityType.
        :param data: The raw data as an OrderedDict.
        """
        if not isinstance(data, collections.OrderedDict):
            raise ex.ParameterError(f'Expected a parameter "data" of type OrderedDict')

        if entity_type == cfg.EntityType.Log:
            fields = ''
        elif entity_type == cfg.EntityType.User:
            fields = TinkDAO.fields_user_input
        elif entity_type == cfg.EntityType.Account:
            fields = TinkDAO.fields_acc_input
        elif entity_type == cfg.EntityType.Transaction:
            fields = TinkDAO.fields_trx_input

        self._entity_type: cfg.EntityType = entity_type
        self._data: collections.OrderedDict = data
        self._fields: tuple = fields

        # Make sure that all expected fields are provided within data
        for f in self._fields:
            if f not in data:
                msg = f'Field {f} expected but not found in data {data}'
                raise AttributeError(msg)

    @property
    def type(self):
        """
        Get the current value of the corresponding property _entity_type.
        :return: The current value of the corresponding property _entity_type.
        """
        return self._entity_type

    @property
    def data(self):
        """
        Get the current value of the corresponding property _data.
        :return: The current value of the corresponding property _data.
        """
        return self._data

    def get_data(self):
        """
        This method returns the data belonging to a single TinkEntity instance.
        :return: The data of a single entity wrapped within an instance of this class.
        """
        data = collections.OrderedDict()
        fields_unmapped_str = ''

        if self._entity_type == cfg.EntityType.User:
            pass
        elif self._entity_type == cfg.EntityType.Account:
            for field in TinkDAO.fields_acc_input:
                if field in TinkDAO.fields_acc_map:
                    # Field to be mapped against the API
                    if field == 'flags':
                        # field "flags" is specified as an array
                        data[field] = list()
                        data[field].append(self.data[field])
                    elif field == 'closed':
                        data[field] = ''
                    elif field == 'payload':
                        data[field] = ''
                    else:
                        if fields_unmapped_str == '':
                            fields_unmapped_str += f'{field}'
                        else:
                            fields_unmapped_str += f', {field}'
                elif field in TinkDAO.fields_acc_api:
                    # Field to be provided to the API as is
                    data[field] = self.data[field]
        elif self._entity_type == cfg.EntityType.Account:
            pass

        if fields_unmapped_str != '':
            raise RuntimeError(f'Unmapped fields in: {str(type(self))} {fields_unmapped_str}')

        return data


class TinkEntityList:
    """
    Object representation of a Tink entity data structure list.
    """

    def __init__(self, entity_type: cfg.EntityType, data_list: list = list()):
        """
        Converts a standard list into a list of TinkEntity object references that
        can be used as an input for the constructor of the class TinkEntityList.
        :param entity_type: The entity type - a value of the Enum config.EntityType.
        :param data_list:  A list of TinkEntity object references or any other typing.
        :return: A list of TinkEntity object references wrapping the input data.
        :raise AttributeError: If 1) data_list is not provided as the expected type or
        2) one of the elements in parameter lst does not conform
        with the the field requirements when trying to create an entity object from it.

        """
        self._entities: TinkEntityList = list()
        self._entity_type: cfg.EntityType = entity_type

        if len(data_list) == 0:
            raise AttributeError(f'Expected a list containing elements in parameter lst')

        for data_item in data_list:
            try:
                entity = TinkEntity(entity_type=self._entity_type, data=data_item)
                self._entities.append(entity)
            except AttributeError as ex_att:
                raise ex_att

    @property
    def type(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._entity_type

    def get_data(self, ext_user_id: str):
        """
        This method returns the contained TinkEntity data.
        :param ext_user_id: The external user reference (this is NOT the Tink internal id).
        If provided then the data returned will be restricted to the records that belong
        to the user ext_user_id.

        :return: The wrapped data as a standard list[OrderedDict]
        this class.
        """
        lst = list()

        # Add all the data to the result list
        if not ext_user_id:
            return self.entities

        # Add only data to the result list if it belongs to the user ext_user_id
        if self._entity_type in (cfg.EntityType.User, cfg.EntityType.Account):
            for entity in self._entities:
                if entity.data['userExternalId'] == ext_user_id:
                    lst.append(entity.get_data())

        return lst

    def contains_data(self, ext_user_id: str):
        """
        This method checks if there is data available for a certain user.

        :param ext_user_id: The external user reference (this is NOT the Tink internal id).
        If provided then the data returned will be restricted to the records that belong
        to the user ext_user_id.

        :return: True if there exists data for ext_user_id, otherwise False
        """
        if len(self.get_data(ext_user_id)) > 0:
            return True
        else:
            return False


class TinkUser(TinkEntity):
    """
    Object representation of a Tink entity data structure list.
    """

    def __init__(self, response=None):
        """
        Initialization
        :param data: The raw user data e.g. received via API
        """
        if not isinstance(response, api.UserResponse):
            msg = f'Expected type of parameter "response" is {type(api.UserResponse)} not {type(response)}'
            raise AttributeError(msg)

        super().__init__(cfg.EntityType.User, response)

        self._attributes = response.data

        self._attributes.update({'userExternalId': response.ex})


