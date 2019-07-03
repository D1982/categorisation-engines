"""Encapsulation of data access for the Tink client."""

import Categorisation.Common.util as util
import Categorisation.Common.config as cfg

import collections
import logging


"""Class that provides data access for the Tink client application.

The Data Access Object is the single point of contact for any interaction with data sources
like files, databases or similar. 
"""


class TinkDAO:

    def __init__(self):
        logging.info("Initiated:" + "TinkDAO.__init__()")

        # Data sources
        self.user_src = 'unbound'
        self.acc_src = 'unbound'
        self.trx_src = 'unbound'

        # Field names of interest
        self.fieldnames_user = ('external_user_id', 'label', 'market', 'locale')
        self.fieldnames_acc = ('userExternalId', 'externalId','availableCredit',
                               'balance', 'name', 'type', 'flags', 'number',
                               'reservedAmount')

        self.fieldnames_trx = ('amount', 'date', 'description', 'externalId',
                               'payload', 'pending', 'tinkId', 'type')


        # Data collections
        self.users = collections.OrderedDict()
        self.accounts = collections.OrderedDict()
        self.transactions = collections.OrderedDict()

        # File handler utility
        self.file_handler = util.FileHandler()


    def bind_data_source(self, src_type, locator):
        if src_type == cfg.TinkEntityType.UserEntity:
            self.user_src = locator
        elif src_type == cfg.TinkEntityType.AccountEntity:
            self.acc_src = locator
        elif src_type == cfg.TinkEntityType.TransactionEntity:
            self.trx_src = locator

    def read_users(self, force_read=True):

        if not self.users or force_read is True:
            data = self.file_handler.read_csv_file(filename=self.user_src, fieldnames=self.fieldnames_user)

            self.users = data  # Returns a List<OrderedDict>

        return self.users

    def read_accounts(self, force_read=True):
        if not self.accounts or force_read is True:
            data = self.file_handler.read_csv_file(filename=self.acc_src, fieldnames=self.fieldnames_acc)

            self.accounts = data  # Returns a List<OrderedDict>

        return self.accounts

    def read_transactions(self, force_read=True):
        if not self.transactions or force_read is True:
            data = self.file_handler.read_csv_file(filename=self.trx_src, fieldnames=self.fieldnames_trx)

            self.transactions = data  # Returns a List<OrderedDict>

        return self.transactions

