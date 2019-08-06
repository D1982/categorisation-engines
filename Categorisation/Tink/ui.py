"""UI components of the Tink client application."""

import Categorisation.Tink.model as model
import Categorisation.Tink.data as data

import Categorisation.Common.config as cfg
import Categorisation.Common.util as utl

import sys
import os
import logging
import datetime

import tkinter as tk
import tkinter.scrolledtext as tkst

from tkinter import filedialog


class TinkUI:

    """
    This class manages the user interface for the Tink Client application.
    The communication with Tinks API goes over a dedicated facade "model".
    The logical communication flow can be considered as follows:
    - ui.TinkUI uses model.TinkModel in order to perform any action
    - model.TinkModel uses data.TinkDAO (Data Access Object) e.g. to read data form files
    - model.TinkModel uses api.* in order to communicate with Tink's API endpoints
    """

    WELCOME_TEXT = 'Tink Client Application started: Please choose an option ...'

    def __init__(self, facade):
        """
        Initialization.

        Hints:
        ---> SetupConfigFrame: Checkbuttons must be setup within the __init__ method
        # Wrapped in a separate method call-backs would not work.

        :param facade: Linked model containing the business logic (instance of class model.TinkModel)
        """
        # Set linked model class instance: Enables the ui callbacks to call the functionality
        # which is encapsulated in the module Categorisation.Common.model
        self._model = facade
        if not isinstance(facade, model.TinkModel):
            self._model = model.TinkModel(data.TinkDAO)

        # Set linked ui class instance: Enables the model class instance to print output on the
        # ui result log using the methods put_result_log(...) and clear_result_log(...)
        self._model.ui = self

        # Create ui elements
        self.create_windows()
        self.create_frames()
        self.setup_file_frame()

        # ---> SetupConfigFrame (See docstring)

        # Widgets
        self.label_config = tk.Label(self.config_frame, bg='lavender', text='Configuration:')
        self.chkbox_delete_val = tk.BooleanVar()
        self.chkbox_delete = tk.Checkbutton(self.config_frame, onvalue=True, offvalue=False,
                                            text='Pre-delete existing data',
                                            variable=self.chkbox_delete_val,
                                            command=self.chkbox_delete_cb)

        self.chkbox_proxy_val = tk.BooleanVar()
        self.chkbox_proxy = tk.Checkbutton(self.config_frame, onvalue=True, offvalue=False,
                                            text='Use a http proxy server',
                                            variable=self.chkbox_proxy_val,
                                            command=self.chkbox_proxy_cb)

        self.entry_proxy = tk.Entry(self.config_frame, width=30)

        # Layout
        self.label_config.grid(row=0, column=1, padx=0, pady=10, sticky=tk.W)
        self.chkbox_delete.grid(row=1, column=1, sticky=tk.W)
        self.chkbox_proxy.grid(row=2, column=1, sticky=tk.W)
        self.entry_proxy.grid(row=2, column=2, sticky=tk.W)

        self.setup_command_frame()
        self.setup_result_frame()
        self.button_command_binding()
        self.ui_data()  # Default values

        # Bind data in the model
        self.data_bindings()

    def create_windows(self):
        """
        Setup the main window.

        :return: void
        """

        # Widgets
        self.window = tk.Tk()
        self.window.title('Tink Client Application for API Testing')

        # Layout
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

    def create_frames(self):
        """
        Setup the frames.

        :return: void
        """
        # Widgets
        self.header_frame = tk.Frame(master=self.window, padx=5, pady=5)
        self.file_frame = tk.Frame(master=self.window, padx=5, pady=5)
        self.config_frame = tk.Frame(master=self.window, padx=5, pady=5)
        self.command_frame = tk.Frame(master=self.window, padx=5, pady=5)
        self.result_frame = tk.Frame(master=self.window, padx=5, pady=5)

        # Layout
        self.file_frame.grid(row=1, sticky=tk.NW)
        self.config_frame.grid(row=2, sticky=tk.NW)
        self.command_frame.grid(row=3, sticky=tk.NW)
        self.result_frame.grid(row=4, sticky=tk.NW)

    def setup_file_frame(self):
        """
        Setup the elements within the file frame.

        :return: void
        """
        # Widgets
        self.label_files = tk.Label(self.file_frame, bg='lavender', text='Files:')

        self.label_file_users = tk.Label(self.file_frame, text='User data:')
        self.label_file_accounts = tk.Label(self.file_frame, text='Account data:')
        self.label_file_trx = tk.Label(self.file_frame, text='Transaction data:')

        self.entry_user_file = tk.Entry(self.file_frame, width=40)
        self.entry_acc_file = tk.Entry(self.file_frame, width=40)
        self.entry_trx_file = tk.Entry(self.file_frame, width=40)

        self.show_userdata_button = tk.Button(self.file_frame, fg='violet', text='Show')
        self.show_accdata_button = tk.Button(self.file_frame, fg='violet', text='Show')
        self.show_trxdata_button = tk.Button(self.file_frame, fg='violet', text='Show')

        # Layout
        self.label_files.grid(row=0, column=1, padx=0, pady=5, sticky=tk.W)

        self.label_file_users.grid(row=1, column=1, sticky=tk.E)
        self.label_file_accounts.grid(row=2, column=1, sticky=tk.E)
        self.label_file_trx.grid(row=3, column=1, sticky=tk.E)

        self.entry_user_file.grid(row=1, column=2, sticky=tk.W)
        self.entry_acc_file.grid(row=2, column=2, sticky=tk.W)
        self.entry_trx_file.grid(row=3, column=2, sticky=tk.W)

        self.show_userdata_button.grid(row=1, column=5, sticky=tk.W)
        self.show_accdata_button.grid(row=2, column=5, sticky=tk.W)
        self.show_trxdata_button.grid(row=3, column=5, sticky=tk.W)

    def setup_config_frame(self):
        """
        Setup the elements within the file frame.

        This frame mainly consists of Checkbuttons that need to be bound to variables
        and callback methods. This does only work correctly if these elements are being
        setup directly within the method __init__(), otherwise callbacks will not work.

        #:return: void
        """
        pass
        # This code  be found in __init__()

    def setup_command_frame(self):
        """
        Setup the elements within the command frame.

        :return: void
        """
        # Widgets
        self.label_commands = tk.Label(self.command_frame, bg='lavender', text='Commands:')
        self.test_button = tk.Button(self.command_frame, fg='orange', text='API health checks')
        self.list_categories_button = tk.Button(self.command_frame, fg='blue', text='List categories')

        self.activate_users_button = tk.Button(self.command_frame, fg='green', text='Create user(s)')
        self.delete_users_button = tk.Button(self.command_frame, fg='red', text='Delete user(s)')

        self.ingest_accounts_button = tk.Button(self.command_frame, fg='green', text='Ingest account(s)')
        self.delete_accounts_button = tk.Button(self.command_frame, fg='red', text='Delete account(s)')
        self.list_accounts_button = tk.Button(self.command_frame, fg='blue', text='List account(s)')

        self.ingest_trx_button = tk.Button(self.command_frame, fg='green', text='Ingest transaction(s)')
        self.delete_trx_button = tk.Button(self.command_frame, fg='red', text='Delete transaction(s)')
        self.list_trx_button = tk.Button(self.command_frame, fg='blue', text='List transaction(s)')

        self.process_button = tk.Button(self.command_frame, fg='brown', text='Process all steps')

        # Layout
        self.label_commands.grid(row=0, column=1, padx=0, pady=10, sticky=tk.W)
        self.test_button.grid(row=1, column=1, sticky=tk.W)
        self.list_categories_button.grid(row=1, column=2, sticky=tk.W)

        self.process_button.grid(row=1, column=2, sticky=tk.W)

        self.activate_users_button.grid(row=3, column=1, sticky=tk.W)
        self.delete_users_button.grid(row=4, column=1, sticky=tk.W)
        self.ingest_accounts_button.grid(row=3, column=2, sticky=tk.W)
        self.delete_accounts_button.grid(row=4, column=2, sticky=tk.W)
        self.list_accounts_button.grid(row=5, column=2, sticky=tk.W)
        self.ingest_trx_button.grid(row=3, column=3, sticky=tk.W)
        self.delete_trx_button.grid(row=4, column=3, sticky=tk.W)
        self.list_trx_button.grid(row=5, column=3, sticky=tk.W)
        self.process_button.grid(row=7, column=1, columnspan=3, sticky=tk.SW)

    def setup_result_frame(self):
        """
        Setup the elements within the result frame.

        :return: void
        """
        # Widgets
        self.label_results = tk.Label(self.result_frame, bg='lavender', text='Results:')
        # self.result_log = tk.Label(master=self.result_frame, anchor=tk.NW, justify=tk.LEFT)
        self.result_log = tkst.ScrolledText(
            master=self.result_frame,
            wrap=tk.WORD,
            width=cfg.UI_STRING_MAX_WITH,
            height=15,
            bg='beige'
        )
        self.save_button = tk.Button(self.result_frame, text='Save logs to file')
        self.clear_button = tk.Button(self.result_frame, text='Clear logs')

        # Layout
        self.label_results.grid(row=0, column=1, padx=0, pady=10, sticky=tk.W)
        self.clear_button.grid(row=1, column=1, sticky=tk.W)
        self.save_button.grid(row=2, column=1, sticky=tk.W)
        self.result_log.grid(row=3, column=1, sticky=tk.W)

    def ui_data(self):
        """
        Initialization of the UI components e.g. with default data.

        :return: void
        """
        # Set User file string
        text = self.entry_user_file
        text.config(state='normal')
        text.insert(0, cfg.IN_FILE_PATTERN_TINK.replace('*', 'Users'))
        text.config(state='readonly')

        # Set Accounts file string
        text = self.entry_acc_file
        text.config(state='normal')
        text.insert(0, cfg.IN_FILE_PATTERN_TINK.replace('*', 'Accounts'))
        text.config(state='readonly')

        # Set Transactions file string
        self.entry_trx_file.config(state='normal')
        self.entry_trx_file.insert(0, cfg.IN_FILE_PATTERN_TINK.replace('*', 'Transactions'))
        self.entry_trx_file.config(state='readonly')

        # Checkbuttons
        self.chkbox_delete.select() # Pre-delete is enabled by default
        self.chkbox_delete_cb()
        self.chkbox_proxy.deselect() # Proxy usage is disabled by default
        self.entry_proxy.config(state='normal')
        self.entry_proxy.insert(0, cfg.PROXY_URL + ':' + cfg.PROXY_PORT)
        self.entry_proxy.config(state='readonly')
        self.put_result_log(text=TinkUI.WELCOME_TEXT, nl=2, time=False)

    def button_command_binding(self):
        """
        Setup event handlers assigning actions to buttons.

        :return: void
        """
        self.show_userdata_button['command'] = self.show_userdata_button_cb
        self.show_accdata_button['command'] = self.show_accdata_button_cb
        self.show_trxdata_button['command'] = self.show_trxdata_button_cb

        self.test_button['command'] = self.test_button_cb
        self.list_categories_button['command'] = self.list_categories_button_cb

        self.activate_users_button['command'] = self.activate_users_button_cb
        self.delete_users_button['command'] = self.delete_users_button_cb
        self.ingest_accounts_button['command'] = self.ingest_accounts_button_cb
        self.delete_accounts_button['command'] = self.delete_accounts_button_cb
        self.list_accounts_button['command'] = self.list_accounts_button_cb
        self.ingest_trx_button['command'] = self.ingest_trx_button_cb
        self.delete_trx_button['command'] = self.delete_trx_button_cb
        self.list_trx_button['command'] = self.list_trx_button_cb
        self.process_button['command'] = self.process_button_cb
        self.clear_button['command'] = self.clear_button_cb
        self.save_button['command'] = self.save_button_cb

    def run(self):
        """
        Main thread running the ui application in the main window.

        :return: void
        """
        self.window.mainloop()

    # --- Event Handlers

    def show_userdata_button_cb(self):
        """
        Event Handler for the corresponding button (equal name).

        :return: void
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        self.put_result_log(text='*** User data ***', clear=True, time=False)
        lst_data = self._model.read_user_data()

        if data:
            text = utl.list_to_string(lst_data)
        else:
            text = 'No data available'

        self.put_result_log(text=text, time=False)

    def show_accdata_button_cb(self):
        """
        Event Handler for the corresponding button (equal name).

        :return: void
        """
        self.put_result_log(text='*** Account data ***', clear=True, time=False)
        lst_data = self._model.read_account_data()

        if data:
            text = utl.list_to_string(lst_data)
        else:
            text = 'No data available'

        self.put_result_log(text=text, time=False)

    def show_trxdata_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        self.put_result_log(text='*** Transaction data ***', clear=True, time=False)
        lst_data = self._model.read_transaction_data()

        if data:
            text = utl.list_to_string(lst_data)
        else:
            text = 'No data available'

        self.put_result_log(text=text, time=False)

    def chkbox_delete_cb(self, event=None):
        """
        Event Handler for the corresponding checkbutton (equal name)

        :param event: reference to the triggering event (not used here)
        :return:
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        val = self.chkbox_delete_val.get()
        self._model.delete_flag = val

    def chkbox_proxy_cb(self, event=None):
        """
        Event Handler for the corresponding checkbutton (equal name)

        :param event: reference to the triggering event (not used here)
        :return:
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        val = self.chkbox_proxy_val.get()
        self._model.proxy_flag = val

    def test_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        # Title
        self.put_result_log(text='*** API Health Checks ***', clear=True, time=False)

        # Logging
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        # Perform action
        rl: model.TinkModelResultList = self._model.test_connectivity()

        # Print results
        self.put_result_log(rl.summary())

    def list_categories_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        # Title
        self.put_result_log(text='*** List categories ***', clear=True, time=False)

        # Logging
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        # Perform action
        rl: model.TinkModelResultList = self._model.list_categories()

        # Print results
        r = rl.first()
        self.put_result_log(r.response.to_string_custom())

    def activate_users_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        # Title
        self.put_result_log(text='*** Activate (create) users ***', clear=True, time=False)

        # Logging
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        # Perform action
        rl: model.TinkModelResultList = self._model.activate_users()

        # Print results
        self.put_result_log(rl.summary(filters={'endpoint': 'user/create'}))

    def delete_users_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        # Title
        self.put_result_log(text='*** Delete users ***', clear=True, time=False)

        # Logging
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        # Perform action
        rl: model.TinkModelResultList = self._model.delete_users()

        # Print results
        self.put_result_log(rl.summary(filters={'endpoint': 'user/delete'}))

    def ingest_accounts_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        # Title
        self.put_result_log(text='*** Ingest accounts ***', clear=True, time=True)

        # Logging
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        # Perform action
        rl: model.TinkModelResultList = self._model.ingest_accounts()

        # Print results
        self.put_result_log(rl.summary(filters={'endpoint': '/accounts'}))

    def delete_accounts_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        # Title
        self.put_result_log(text='*** Delete accounts ***', clear=True, time=True)

        # Logging
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        self.put_result_log('NOT YET IMPLEMENTED')

    def list_accounts_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        # Title
        self.put_result_log(text='*** List accounts ***', clear=True, time=True)

        # Logging
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        self.put_result_log('NOT YET IMPLEMENTED')

    def ingest_trx_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        # Title
        self.put_result_log(text='*** Ingest transactions ***', clear=True, time=True)

        # Logging
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        self.put_result_log('NOT YET IMPLEMENTED')

    def delete_trx_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        # Title
        self.put_result_log(text='*** Delete transactions ***', clear=True, time=True)

        # Logging
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        self.put_result_log('NOT YET IMPLEMENTED')

    def list_trx_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        # Title
        self.put_result_log(text='*** List transactions ***', clear=True, time=True)

        # Logging
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        self.put_result_log('NOT YET IMPLEMENTED')

    def process_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        # Title
        self.put_result_log(text='*** Process full workflow ***', clear=True, time=True)

        # Logging
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        # Perform actions
        rl1: model.TinkModelResultList = self._model.delete_users()
        self.put_result_log(rl1.summary(filters={'endpoint': 'user/delete'}))

        self.put_result_log(text=os.linesep, time=False)

        rl2: model.TinkModelResultList = self._model.activate_users()
        self.put_result_log(rl2.summary(filters={'endpoint': 'user/create'}))


    def clear_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        self.clear_result_log()

    def save_button_cb(self):
        """
        Event Handler for the corresponding button (equal name)

        :return: void
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        type_list = [('Text files', '*.txt')]
        file_name = filedialog.asksaveasfilename(
            filetypes=type_list, defaultextension='*.txt'
        )
        # Save file if user entered a file name
        if file_name != '':
            with open(file_name, 'w') as output_file:
                output_file.writelines(self.result_log.get(1.0, tk.END))

    def data_bindings(self):
        """
        Data bindings to provide required input data to the data access object.
        Currently the source data locations are solely files).

        :return: void
        """
        # Provide required input data to the data access object (source data locations, here files)
        self._model.dao.bind_data_source(cfg.TinkEntityType.UserEntity, self.entry_user_file.get())
        self._model.dao.bind_data_source(cfg.TinkEntityType.AccountEntity, self.entry_acc_file.get())
        self._model.dao.bind_data_source(cfg.TinkEntityType.TransactionEntity, self.entry_trx_file.get())

    # --- Helpers
    def put_result_log(self, text: str, clear=False, nl: int = 1, time=True, scroll=False):
        """
        Write to the output (in the ui log area).

        :param text: the text to be displayed in the ui log area.
        :param clear: flag indicating whether to clear the log before printing.
        :param nl: number of newlines between the current text and the new text
        :param time: flag indicating whether to show the time at the beginning of the line
        :param scroll: flag indicating whether to scroll automatically with the text

        :return: void
        """
        if clear:
            self.clear_result_log()

        if time:
            date_time = utl.strdate(datetime.datetime.now()) + ': '
        else:
            date_time = ''

        self.result_log.insert(tk.INSERT, date_time + text + os.linesep * nl)

        if scroll:
            self.result_log.see(tk.END)

    def clear_result_log(self):
        """
        Clear the output (in the ui log area).

        :return: void
        """
        self.result_log.delete(1.0, tk.END)
