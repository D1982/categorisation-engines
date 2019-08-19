"""Encapsulation of data access for the Tink client."""

import Categorisation.Common.util as util
import Categorisation.Common.config as cfg
import Categorisation.Tink.data as data
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

    fields_user_src_in = ('userExternalId', 'label', 'market', 'locale')

    fields_user_map = tuple

    fields_user_api_in = ('userExternalId', 'label', 'market', 'locale')

    fields_user_api_out = ('userExternalId', 'label', 'market', 'locale',
                           'id', 'timeZone', 'currency', 'created')

    # Standard fields for entity Account

    fields_acc_src_in = ('userExternalId', 'externalId', 'availableCredit', 'balance',
                         'name', 'type', 'flags', 'number', 'reservedAmount')

    fields_acc_map = ('flags',)

    fields_acc_api_in = ('externalId', 'availableCredit', 'balance',
                         'name', 'type', 'flags', 'number', 'reservedAmount')

    fields_acc_api_out = ('externalId', 'availableCredit', 'balance', 'closed',
                          'name', 'type', 'flags', 'number', 'reservedAmount', 'payload')

    # Standard fields for entity Transaction

    fields_trx_input = ('amount', 'date', 'description', 'externalId', 'payload',
                        'pending', 'tinkId', 'type', 'n26cat', 'currency')

    fields_trx_map = ('amount', 'date', 'description', 'externalId', 'payload',
                      'pending', 'tinkId', 'type', 'n26cat', 'currency')

    fields_trx_api_in = tuple

    fields_trx_api_out = tuple

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

    def load_input(self, entity_type: cfg.EntityType,
                   source_type: cfg.DataProviderType,
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

        if source_type != cfg.DataProviderType.File:
            msg = f'Input source types other than {cfg.DataProviderType.File} are not yet supported'
            raise NotImplementedError(msg)

        if entity_type == cfg.EntityType.Log:
            locator = cfg.TINK_LOGFILE
        elif entity_type == cfg.EntityType.User:
            input_data = self._users_input
            locator = cfg.TinkConfig.get_instance().user_source
            fields = TinkDAO.fields_user_src_in
        elif entity_type == cfg.EntityType.Account:
            input_data = self._accounts_input
            locator = cfg.TinkConfig.get_instance().account_source
            fields = TinkDAO.fields_acc_src_in
        elif entity_type == cfg.EntityType.Transaction:
            input_data = self._transactions_input
            locator = cfg.TinkConfig.get_instance().transaction_source
            fields = TinkDAO.fields_trx_input

        if not input_data or force_read is True:
            try:
                input_data = self.file_handler.read_csv_file(filename=locator,
                                                             fieldnames=fields)
            except Exception as e:
                raise e

        if entity_type == cfg.EntityType.User:
            self._users_input = input_data
        elif entity_type == cfg.EntityType.Account:
            self._accounts_input = input_data
        elif entity_type == cfg.EntityType.Transaction:
            self._transactions_input = input_data

        return input_data

    def dump_output(self, entity_type: cfg.EntityType, source_type: cfg.DataProviderType):
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

        if source_type != cfg.DataProviderType.File:
            msg = f'Input source types other than {cfg.DataProviderType.File} are not yet supported'
            raise NotImplementedError(msg)

        if entity_type == cfg.EntityType.Log:
            locator = cfg.TINK_LOGFILE
        elif entity_type == cfg.EntityType.User:
            output_data = self._users
            locator = cfg.TinkConfig.get_instance().user_target
            fields = TinkDAO.fields_user_api_out
        elif entity_type == cfg.EntityType.Account:
            output_data = self._accounts
            locator = cfg.TinkConfig.get_instance().account_target
            fields = TinkDAO.fields_acc_api_out
        elif entity_type == cfg.EntityType.Transaction:
            output_data = self._transactions
            locator = cfg.TinkConfig.get_instance().transaction_target
            fields = TinkDAO.fields_trx_api_out

        try:
            self.file_handler.write_csv_file(data=output_data.data,
                                             fieldnames=fields,
                                             filename=locator)
        except Exception as e:
            raise e

        return data

    @property
    def users(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._users

    @users.setter
    def users(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._users = value

    @property
    def accounts(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._accounts

    @accounts.setter
    def accounts(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._accounts = value

    @property
    def transactions(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        self._transactions

    @transactions.setter
    def transactions(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._transactions = value


class TinkEntity(metaclass=abc.ABCMeta):

    """
    Object representation of a Tink entity data structure.
    """

    @staticmethod
    @abc.abstractmethod
    def create_from_http_response(response):
        """
        This is a static factory mehotd that creates a TinkEntity object from
        a http response originated from an appropriate Tink API endpoint.
        :param response: A response of a supported sub-type of TinkAPIResponse
        containing the data.
        :raise NotImplementedError: If the function has not been implemented within
        a derived class.
        """
        raise NotImplementedError

    def __init__(self,
                 entity_type: cfg.EntityType,
                 entity_data: dict = None,
                 fields: tuple = None):
        """
        Initialization.
        :param entity_type: The entity type - a value of the Enum config.EntityType.
        :param entity_data: The raw data as an OrderedDict.
        :raise ParameterError: If not all the parameters were delivered with
        the expected data type.
        :raise AttributeError: If at least one of the expected fields was not
        provided i.e. could not be found in the given data.
        """

        if not isinstance(entity_data, dict):
            raise ex.ParameterError(param_name='data',
                                    expected_type=type(dict()),
                                    found_type=type(entity_data),
                                    result_list=None)

        self._entity_type: cfg.EntityType = entity_type
        self._data: dict = entity_data
        self._fields: tuple = fields

        if 'userExternalId' in self._data:
            self._ext_user_id = self._data['userExternalId']
        else:
            self._ext_user_id = None

        self.adjust_data()

        # Make sure that the least expected fields are provided within data
        for f in self._fields:
            if f not in entity_data:
                msg = f'Field "{f}" expected but not found in "data" {entity_data}'
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
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._data

    @property
    def ext_user_id(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._ext_user_id

    @abc.abstractmethod
    def adjust_data(self):
        """
        This method adjusts the contained data adding missing fields and/or removing
        unnecessary fields.
        Example: If there was data provided by any input data source there might
        still be missing some fields e.g. in order to ingest the data into the
        Tink platform over a dedicated API. This method will fill the gaps.

        See the static members fields.* of class data.TinkDAO driving the data
        enrichment process.
        :return: Void
        """
        raise NotImplementedError


class TinkEntityList:
    """
    Object representation of a Tink entity data structure list.
    """

    def __init__(self, entity_type: cfg.EntityType, entity_data: list = None, fields: tuple = None):
        """
        Converts a standard list into a list of TinkEntity object references that
        can be used as an input for the constructor of the class TinkEntityList.
        :param entity_type: The entity type - a value of the Enum config.EntityType.
        :param entity_data: The raw data as a dictionary. The data should usually
        originate either from a data source or from the Tink API.
        :param fields: A list (tuple) of relevant fields to be extracted out of
        the provided data in order to mak the information accessible in
        a structured way over this data access object.
        :raise ParameterError: If not all the parameters were delivered with
        the expected data type.
        :raise AttributeError: If not all the fields specified could be found
        within the provided data.

        """
        self._entities: TinkEntityList = list()
        self._entity_type: cfg.EntityType = entity_type

        if not isinstance(entity_data, list):
            raise ex.ParameterError(param_name='entity_data',
                                    expected_type=type(list()),
                                    found_type=type(entity_data),
                                    result_list=None)

        if not isinstance(fields, tuple):
            raise ex.ParameterError(param_name='data',
                                    expected_type=type(list()),
                                    found_type=type(fields),
                                    result_list=None)

        for item in entity_data:
            try:
                if self._entity_type == cfg.EntityType.User:
                    entity = TinkUser(user_data=item, fields=fields)
                elif self._entity_type == cfg.EntityType.Account:
                    entity = TinkAccount(acc_data=item, fields=fields)
                else:
                    pass
                    # TODO: Add transaction case here once class TinkTransaction is available
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

    @property
    def data(self):
        """
        Get the total payload stored in all entities within this TinkEntityList.
        :return: The current value of the corresponding property _<method_name>.
        """
        result_data = list()
        for entity in self._entities:
            result_data.append(entity.data)

        return result_data

    def get_data(self, ext_user_id: str = None):
        """
        This method returns the contained TinkEntity data.
        :param ext_user_id: The external user reference (this is NOT the Tink internal id).
        If provided then the data returned will be restricted to the records that belong
        to the user ext_user_id.

        :return: The wrapped data as a standard list[dict]
        this class.
        """
        lst = list()

        # Add all the data to the result list
        if not ext_user_id:
            return self._entities

        # Add only data to the result list if it belongs to the user ext_user_id
        if self._entity_type in (cfg.EntityType.User, cfg.EntityType.Account):
            for entity in self._entities:
                if entity.ext_user_id == ext_user_id:
                    lst.append(entity.data)

        return lst

    def contains_data(self, ext_user_id: str):
        """
        This method checks if there is data available for a certain user.
        :param ext_user_id: The external user reference (this is NOT the Tink internal id).
        :return: True if there exists data for ext_user_id, otherwise False
        """
        if len(self.get_data(ext_user_id)) > 0:
            return True
        else:
            return False


@TinkEntity.register
class TinkUser(TinkEntity):
    """
    Object representation of a Tink entity data structure list.
    """

    @staticmethod
    def create_from_http_response(response):
        """
        Creates a TinkEntity object from a http response originated from
        a Tink API endpoint.
        :param response: A response of a supported sub-type of TinkAPIResponse
        containing the data.
        :raise ParameterError: If the supplied response object is not a
        supported response. This does basically mean that the response cannot
        become a valid TinkUser object.
        """
        supported_responses = api.UserResponse + api.UserActivationResponse

        if isinstance(response, api.UserResponse):
            fields = api.UserResponse.fields
        elif isinstance(response, api.UserActivationResponse):
            fields = api.UserActivationResponse.fields
        else:
            raise ex.ParameterError(param_name='response',
                                    expected_type=supported_responses,
                                    found_type=type(response),
                                    result_list=None)

        return TinkUser(user_data=response.data, fields=fields)

    def __init__(self, user_data: dict, fields: tuple):
        """
        Initialization
        :param user_data: The raw data as a dictionary. The data should usually
        originate either from a data source or from the Tink API.
        :param fields: A list (tuple) of relevant fields to be extracted out of
        the provided data in order to mak the information accessible in
        a structured way over this data access object.
        :raise ParameterError: If not all the parameters were delivered with
        the expected data type.
        :raise AttributeError: If at least one of the expected fields was not
        provided i.e. could not be found in the given data.
        """
        super().__init__(entity_type=cfg.EntityType.User, entity_data=user_data, fields=fields)

    def adjust_data(self):
        pass

@TinkEntity.register
class TinkAccount(TinkEntity):
    """
    Object representation of a Tink entity data structure list.
    """

    @staticmethod
    def create_from_http_response(response):
        """
        Creates a TinkEntity object from a http response originated from
        a Tink API endpoint.
        :param response: A response of a supported sub-type of TinkAPIResponse
        containing the data.
        :raise ParameterError: If the supplied response object is not a
        supported response. This does basically mean that the response cannot
        become a valid TinkUser object.
        """
        supported_responses = api.AccountIngestionResponse + api.AccountListResponse

        if isinstance(response, api.AccountIngestionResponse):
            fields = api.AccountIngestionResponse.fields
        elif isinstance(response, api.AccountListResponse):
            fields = api.AccountListResponse.fields
        else:
            raise ex.ParameterError(param_name='response',
                                    expected_type=supported_responses,
                                    found_type=type(response),
                                    result_list=None)

        return TinkAccount(acc_data=response._data, fields=fields)

    def __init__(self, acc_data: dict, fields: tuple):
        """
        Initialization
        :param acc_data: The raw data as a dictionary. The data should usually
        originate either from a data source or from the Tink API.
        :param fields: A list (tuple) of relevant fields to be extracted out of
        the provided data in order to mak the information accessible in
        a structured way over this data access object.
        :raise ParameterError: If not all the parameters were delivered with
        the expected data type.
        :raise AttributeError: If at least one of the expected fields was not
        provided i.e. could not be found in the given data.
        """
        super().__init__(entity_type=cfg.EntityType.Account, entity_data=acc_data, fields=fields)

    def adjust_data(self):
        fields_unmapped_str = ''

        # Remove fields that are not required
        for k in list(self._data.keys()):
            if k not in self._fields:
                del self._data[k]

        for field in self._fields:
            if field in self._data:
                value = self._data[field]

            if field in TinkDAO.fields_acc_map:
                # Field to be mapped against the API
                if field == 'flags':  # Specified as an array
                    self._data[field] = list()
                    self._data[field].append(value)
                elif field == 'closed':
                    self._data[field] = ''
                elif field == 'payload':
                    self._data[field] = ''
                else:
                    if fields_unmapped_str == '':
                        fields_unmapped_str += f'{field}'
                    else:
                        fields_unmapped_str += f', {field}'

        if fields_unmapped_str != '':
            raise RuntimeError(f'Unmapped fields in: {str(type(self))} {fields_unmapped_str}')
