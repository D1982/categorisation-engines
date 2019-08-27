"""Encapsulation of data access for the Tink client."""

import Categorisation.Common.util as util
import Categorisation.Common.config as cfg
import Categorisation.Tink.data as data
import Categorisation.Tink.model as model

import Categorisation.Common.exceptions as ex
import Categorisation.Tink.api as api
import sys
import collections
import logging
import abc  # https://pymotw.com/3/abc/
from datetime import datetime


class TinkDAO:

    """
    Class that provides data access for the Tink client application.

    The Data Access Object is the single point of contact for any interaction with data sources
    like files, databases or similar.

    """
    # Constants for Data Access R/W

    READ = 'READ'

    WRITE = 'WRITE'

    # Standard fields for entity User

    fields_user_src_in = ('userExternalId', 'label', 'market', 'locale')

    fields_user_map = tuple

    fields_user_api_in = ('userExternalId', 'label', 'market', 'locale')

    fields_user_api_out = ('userExternalId', 'label', 'market', 'locale',
                           'id', 'timeZone', 'currency', 'created', 'errorMessage', 'errorCode')

    # Standard fields for entity Account

    fields_acc_src_in = ('userExternalId', 'externalId', 'availableCredit', 'balance',
                         'name', 'type', 'flags', 'number', 'reservedAmount',
                         'payloadTags')

    fields_acc_map = ('flags', 'payload')

    fields_acc_add = ('payloadCreated',)

    fields_acc_api_in = ('externalId', 'availableCredit', 'balance',
                         'name', 'type', 'flags', 'number', 'reservedAmount',
                         'payloadTags', 'payloadCreated')

    fields_acc_api_out = ('accountNumber', 'availableCredit', 'balance', 'bankId',
                          'credentialsId', 'id', 'name', 'type', 'userId', 'currencyCode',
                          'errorMessage', 'errorCode')  # 'payloadTags', 'payloadCreated'

    # Standard fields for entity Transaction

    fields_trx_input = ('amount', 'date', 'description', 'externalId', 'payload',
                        'pending', 'tinkId', 'type', 'n26cat', 'currency')

    fields_trx_map = ('amount', 'date', 'description', 'externalId', 'payload',
                      'pending', 'tinkId', 'type', 'n26cat', 'currency')

    fields_trx_api_in = tuple

    fields_trx_api_out = tuple

    def __init__(self, data_provider: cfg.DataProviderType = cfg.DataProviderType.File):
        """
        Creates a new data access object connected to the given data provider.
        :param data_provider: Data provider type - a value of the Enum config.DataProviderType.
        """
        if data_provider != cfg.DataProviderType.File:
            msg = f' Data providers other than {cfg.DataProviderType.File}" are not (yet) supported'
            raise NotImplementedError(msg)

        self._data_provider = data_provider
        self._config = cfg.TinkConfig.get_instance()

        # Data collections

        self._logs: list = list()
        self._users: TinkEntityList = None
        self._accounts: TinkEntityList = None
        self._transactions: TinkEntityList = None

        self._tink_users: TinkEntityList = None
        self._tink_accounts: TinkEntityList = None
        self._tink_transactions: TinkEntityList = None

        # Instance of a file handler utility

        self.file_handler = util.FileHandler()

    def data_access(self,
                    access_type: str = READ,
                    entity_type: cfg.EntityType = None,
                    locator: str = None,
                    fields: tuple = None,
                    payload=None):
        """
        :param access_type: The data access type (TinkDAO.READ or TinkDAO.WRITE).
        :param entity_type: The entity type of interest - a value of the Enum config.EntityType.
        :param locator: Locator of the data provider (e.g. a file path).
        :param fields: A list (tuple) of relevant fields within the data to be read or written (payload).
        :param payload: The (raw) data to be stored.
        :return: The data that was read/written.
        :raise NotImplementedError: If a function has not been implemented so far or
        :raise AttributeError: If at least one of the expected fields was not
        provided i.e. could not be found in the given data.
        :raise Exception: Any other error that might occur in a method invoced within this
        method will be caught and raised.
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)
        logging.info(f'access_type: {access_type}')
        logging.info(f'entity_type: {entity_type.value}')
        logging.info(f'locator: {locator}')
        logging.info(f'fields: {fields}')

        if access_type not in (TinkDAO.READ, TinkDAO.WRITE):
            msg = f'Unexpected access type "{access_type}"'
            raise AttributeError(msg)

        if entity_type not in cfg.EntityType:
            msg = f' Entity type {entity_type}" not (yet) supported'
            raise NotImplementedError(msg)

        if not locator:
            msg = f'Missing locator for data access.'
            raise NotImplementedError(msg)

        if not fields:
            msg = f'Please specify the fields of interest.'
            raise NotImplementedError(msg)

        # File access
        if self._data_provider == cfg.DataProviderType.File:
            if access_type == TinkDAO.READ:
                try:
                    data_raw = self.file_handler.read_csv_file(filename=locator,
                                                               fieldnames=fields,
                                                               skip_header=True)
                except Exception as e:
                    raise e

                return data_raw

            elif access_type == TinkDAO.WRITE:
                if not payload:
                    msg = f'Missing parameter payload for access_type "{access_type}"'
                    raise Exception(msg)

                try:
                    self.file_handler.write_csv_file(filename=locator,
                                                     fieldnames=fields,
                                                     data=payload)
                except Exception as e:
                    raise e

                return payload

    @property
    def data_provider(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._data_provider

    @property
    def logs(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._logs

    @property
    def users(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        if not self._users or not self._users.contains_entities():
            try:
                raw_data = self.data_access(entity_type=cfg.EntityType.User,
                                            access_type=data.TinkDAO.READ,
                                            locator=self._config.user_source,
                                            fields=TinkDAO.fields_user_src_in)

                self.users = raw_data
            except Exception as e:
                raise e

        return self._users

    @users.setter
    def users(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        :raise Exception: If there occurred an error when trying to set the value.
        """
        if isinstance(value, TinkEntityList):
            self._users = value
        else:
            try:
                entities = TinkEntityList(entity_type=cfg.EntityType.User,
                                          entity_data=value,
                                          fields=data.TinkDAO.fields_user_src_in)
                self._users = entities
            except Exception as e:
                raise e

    @property
    def accounts(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        if not self._accounts or not self._accounts.contains_entities():
            try:
                raw_data = self.data_access(entity_type=cfg.EntityType.Account,
                                            access_type=data.TinkDAO.READ,
                                            locator=self._config.account_source,
                                            fields=TinkDAO.fields_acc_src_in)

                self.accounts = raw_data
            except Exception as e:
                raise e

        return self._accounts

    @accounts.setter
    def accounts(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        if isinstance(value, TinkEntityList):
            self._accounts = value
        else:
            try:
                entities = TinkEntityList(entity_type=cfg.EntityType.Account,
                                          entity_data=value,
                                          fields=data.TinkDAO.fields_acc_src_in)
                self._accounts = entities
            except Exception as e:
                raise e

    @property
    def transactions(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        if not self._transactions or not self._transactions.contains_entities():
            try:
                raw_data = self.data_access(entity_type=cfg.EntityType.Transaction,
                                            access_type=data.TinkDAO.READ,
                                            locator=self._config.trx_source,
                                            fields=TinkDAO.fields_trx_src_in)

                self.transactions = raw_data
            except Exception as e:
                raise e

        return self._transactions

    @transactions.setter
    def transactions(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        if isinstance(value, TinkEntityList):
            self._transactions = value
        else:
            try:
                entities = TinkEntityList(entity_type=cfg.EntityType.Transaction,
                                          entity_data=value,
                                          fields=data.TinkDAO.fields_transaction_src_in)
                self._transactions = entities
            except Exception as e:
                raise e

    @property
    def tink_users(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._tink_users

    @tink_users.setter
    def tink_users(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        if isinstance(value, TinkEntityList):
            self._tink_users = value
        else:
            try:
                entities = TinkEntityList(entity_type=cfg.EntityType.User,
                                          entity_data=value,
                                          fields=data.TinkDAO.fields_user_src_in)
                self._tink_users = entities
            except Exception as e:
                raise e

    @property
    def tink_accounts(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._tink_accounts

    @tink_accounts.setter
    def tink_accounts(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        if isinstance(value, TinkEntityList):
            self._tink_accounts = value
        else:
            try:
                # TODO: Here I am #1
                entities = TinkEntityList(entity_type=cfg.EntityType.Account,
                                          entity_data=value,
                                          fields=data.TinkDAO.fields_acc_api_out)
                self._tink_accounts = entities
            except Exception as e:
                raise e

    @property
    def tink_transactions(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._tink_transactions

    @tink_transactions.setter
    def tink_transactions(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        if isinstance(value, TinkEntityList):
            self._tink_transactions = value
        else:
            try:
                entities = TinkEntityList(entity_type=cfg.EntityType.Transaction,
                                          entity_data=value,
                                          fields=data.TinkDAO.fields_trx_src_in)
                self._tink_transactions = entities
            except Exception as e:
                raise e


class TinkEntity(metaclass=abc.ABCMeta):

    """
    Object representation of a Tink entity data structure.
    """

    @staticmethod
    @abc.abstractmethod
    def create_from_http_response(response):
        """
        This is a static factory method that creates a TinkEntity object from
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
            raise ex.ParameterTypeError(param_name='entity_data',
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

    @staticmethod
    @abc.abstractmethod
    def create_from_http_response(response):
        """
        This is a static factory method that creates a TinkEntityList object from
        a http response originated from an appropriate Tink API endpoint.
        :param response: A response of a supported sub-type of TinkAPIResponse
        containing the data.
        :raise NotImplementedError: If the function has not been implemented within
        a derived class.
        """
        supported_responses = api.AccountListResponse

        if isinstance(response, api.AccountListResponse):
            fields = api.AccountListResponse.fieldnames
        else:
            raise ex.ParameterTypeError(param_name='response',
                                        expected_type=supported_responses,
                                        found_type=type(response),
                                        result_list=None)

        if isinstance(response.payload, list):
            entity_lst = list()
            for item in response.payload:
                item.update({'userExternalId': str(response.request.ext_user_id)})
                for field in fields:
                    if field in response.payload:
                        item.update({field: response.payload[field]})
                entity_lst.append(item)
        else:
            raise RuntimeError(f'Was expecting a payload of type {type(list)} for {type(response)}')

        return TinkEntityList(entity_type=cfg.EntityType.Account,
                              entity_data=entity_lst,
                              fields=fields)

    def __init__(self, entity_type: cfg.EntityType, entity_data: list = list(), fields: tuple = tuple()):
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
        self._entities: TinkEntity = list()
        self._entity_type: cfg.EntityType = entity_type
        self._fields: tuple = fields

        if not isinstance(entity_data, list):
            raise ex.ParameterTypeError(param_name='entity_data',
                                        expected_type=type(list()),
                                        found_type=type(entity_data),
                                        result_list=None)

        if not isinstance(fields, tuple):
            raise ex.ParameterTypeError(param_name='fields',
                                        expected_type=type(list()),
                                        found_type=type(fields),
                                        result_list=None)

        if not entity_data or len(entity_data) == 0:
            return

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

    @property
    def fields(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._fields

    @fields.setter
    def fields(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        :raise Exception: If there occurred an error when trying to set the value.
        """
        self._fields = value


    @property
    def entities(self):
        """
        Get a list containing all the entities stored within this TinkEntityList object.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._entities

    def append(self, entity_list):
        """
        Appends the contents of a given TinkEntityList to the current instance.
        :param entity_list: Another instance of TinkEntityList holding entities
        that should be appended to the list of entities held in this TinkEntityList.
        """
        if not isinstance(entity_list, TinkEntityList):
            raise ex.ParameterTypeError(param_name='entity_list',
                                        expected_type=type(TinkEntityList),
                                        found_type=type(entity_list),
                                        result_list=None)

        if len(entity_list.entities) > 0:
            self._entities.extend(entity_list.entities)

    def create_subset(self, ext_user_id: str = None):
        """
        Creates a new TinkEntityList that is a subset of the current one restricted to the
        entities that belong to a given user ext_user_id.
        :param ext_user_id: The external user reference (this is NOT the Tink internal id).
        If provided then the data returned will be restricted to the records that belong
        to the user ext_user_id.
        :return: A new TinkEntityList restricted to the entities that belong to the given
        user ext_user_id.
        :raise Exception: If an error occured when trying to instantiate a new
        TinkEntityList with the gathered data.
        """
        subset_entities = self.get_entities(ext_user_id=ext_user_id)

        try:
            subset_instance = TinkEntityList(entity_type=self._entity_type,
                                             entity_data=subset_entities,
                                             fields=self._fields)
            return subset_instance
        except Exception as e:
            logging.error(e)
            return self




    def get_entities(self, ext_user_id: str = None):
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

    def contains_entities(self, ext_user_id: str = None):
        """
        This method checks if there is any data available.
        :param ext_user_id: The external user reference (this is NOT the Tink internal id).
        The result of the method will depend from whether there exists data for a given
        user.
        :return: True if there exists data, otherwise False
        """
        if len(self.get_entities(ext_user_id)) > 0:
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
            fields = api.UserResponse.fieldnames
        elif isinstance(response, api.UserActivationResponse):
            fields = api.UserActivationResponse.fieldnames
        else:
            raise ex.ParameterTypeError(param_name='response',
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
        raise ex.ParameterTypeError(param_name='response',
                                    expected_type=None,
                                    found_type=type(response),
                                    result_list=None)

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

        # Check availability of all expected fields
        for field in self._fields:
            if field in self._data:
                value = self._data[field]
            # Check if an input fields requires any mapping operations
            if field in TinkDAO.fields_acc_map:
                # TODO: #DevWork: Add all the required mapping code in this section
                if field == 'flags':  # Specified as an array
                    my_list = self._data[field].split(",")
                    self._data[field] = my_list
                elif field == 'payloadTags':  # Specified as an array
                    my_list = self._data[field].split(",")
                    self._data[field] = my_list
                else:
                    if fields_unmapped_str == '':
                        fields_unmapped_str += f'{field}'
                    else:
                        fields_unmapped_str += f', {field}'

        # Add fields that are not gathered from the input data. These must be mentioned in map
        for field in data.TinkDAO.fields_acc_add:
            # TODO: #DevWork: Add all the required mapping code in this section
            if field == 'payloadCreated' and field in self._fields:
                self._data['payloadCreated'] = util.strdate(datetime.now())

        if fields_unmapped_str != '':
            raise RuntimeError(f'Unmapped fields in: {str(type(self))} {fields_unmapped_str}')
