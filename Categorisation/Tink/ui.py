"""UI components of the Tink client application."""

import Categorisation.Tink.model as model
import Categorisation.Tink.data as data

import Categorisation.Common.config as cfg
import Categorisation.Common.util as utl

import sys
import os
import logging
import datetime
import time
import traceback
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

    TITLE = 'Tink Client Application for API Testing'
    WELCOME_TEXT = 'Tink Client Application started: Please choose an option ...'

    def __init__(self, model_facade):
        """
        Initialization.

        Hints:
        ---> SetupConfigFrame: Checkbuttons must be setup within the __init__ method
        # Wrapped in a separate method call-backs would not work.

        :param model_facade: Linked model containing the business logic (instance of class model.TinkModel)
        """
        # --- Model and DAO

        # Set linked model class instance: Enables the ui callbacks to call the functionality
        # which is encapsulated in the module Categorisation.Common.model
        self._model = model_facade
        if not isinstance(model_facade, model.TinkModel):
            self._model = model_facade.TinkModel(data.TinkDAO)

        # --- Windows
        self.window = tk.Tk()
        self.window.title(TinkUI.TITLE)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # --- Frames: Widgets
        self.frm_header = tk.Frame(master=self.window, padx=5, pady=5)
        self.frm_file = tk.Frame(master=self.window, padx=5, pady=5)
        self.frm_config = tk.Frame(master=self.window, padx=5, pady=5)
        self.frm_command = tk.Frame(master=self.window, padx=5, pady=5)
        self.frm_result = tk.Frame(master=self.window, padx=5, pady=5)

        # --- Frames: Layout
        self.frm_file.grid(row=1, sticky=tk.NW)
        self.frm_config.grid(row=2, sticky=tk.NW)
        self.frm_command.grid(row=3, sticky=tk.NW)
        self.frm_result.grid(row=4, sticky=tk.NW)

        # --- Variables to hold widget data
        self.cbtn_result_file_val = tk.BooleanVar()
        self.cbtn_proxy_val = tk.BooleanVar()
        self.cbtn_delete_val = tk.BooleanVar()
        self.opt_msg_level_det_val = tk.StringVar()

        # --- UI widgets and Layout
        self._widgets()
        self._layout()

        # --- UI Data Initialization and Synchronization
        self._data_init()
        self._data_sync()

    def _widgets(self):
        """
        Setup the ui widgets.
        :return: Void
        """
        # --- File Frame: Input Files - Text Fields
        self.txt_usr_file_in = tk.Entry(master=self.frm_file,
                                        width=40,
                                        state='normal')

        self.txt_acc_file_in = tk.Entry(master=self.frm_file,
                                        width=40,
                                        state='normal')

        self.txt_trx_file_in = tk.Entry(master=self.frm_file,
                                        width=40,
                                        state='normal')

        # --- File Frame: Input Files - Action Buttons
        self.btn_usr_file_in = tk.Button(master=self.frm_file,
                                         fg='violet',
                                         text='Show',
                                         command=lambda: self._callback('btn_usr_file_in'))

        self.btn_acc_file_in = tk.Button(master=self.frm_file,
                                         fg='violet',
                                         text='Show',
                                         command=lambda: self._callback('btn_acc_file_in'))

        self.btn_trx_file_in = tk.Button(master=self.frm_file,
                                         fg='violet',
                                         text='Show',
                                         command=lambda: self._callback('btn_trx_file_in'))

        # --- File Frame: Output Files - Text Fields
        self.txt_usr_file_out = tk.Entry(master=self.frm_file,
                                         width=40,
                                         state='normal')

        self.txt_acc_file_out = tk.Entry(master=self.frm_file,
                                         width=40,
                                         state='normal')

        self.txt_trx_file_out = tk.Entry(master=self.frm_file,
                                         width=40,
                                         state='normal')

        # --- File Frame: Output Files - Action Buttons
        self.btn_usr_file_out = tk.Button(master=self.frm_file,
                                          fg='violet',
                                          text='Show',
                                          command=lambda: self._callback('btn_usr_file_out'))

        self.btn_acc_file_out = tk.Button(master=self.frm_file,
                                          fg='violet',
                                          text='Show',
                                          command=lambda: self._callback('btn_acc_file_out'))

        self.btn_trx_file_out = tk.Button(master=self.frm_file,
                                          fg='violet',
                                          text='Show',
                                          command=lambda: self._callback('btn_trx_file_out'))

        # --- Config Frame: Checkboxes
        self.cbtn_result_file = tk.Checkbutton(self.frm_config,
                                               onvalue=True,
                                               offvalue=False,
                                               text='Write results into files',
                                               variable=self.cbtn_result_file_val,
                                               command=lambda: self._callback('cbtn_result_file'))

        self.cbtn_delete = tk.Checkbutton(self.frm_config,
                                          onvalue=True,
                                          offvalue=False,
                                          text='Delete existing data',
                                          variable=self.cbtn_delete_val,
                                          command=lambda: self._callback('cbtn_delete'))

        self.cbtn_proxy = tk.Checkbutton(master=self.frm_config,
                                         onvalue=True,
                                         offvalue=False,
                                         text='Use HTTP proxy',
                                         variable=self.cbtn_proxy_val,
                                         command=lambda: self._callback('cbtn_proxy'))
        self.cbtn_delete.grid(row=1, column=1, sticky=tk.W)

        # --- Config Frame: Text Widgets

        self.txt_proxy = tk.Entry(self.frm_config, width=30)

        # --- Command Frame: Button Widgets

        self.btn_test = tk.Button(master=self.frm_command,
                                  fg='orange',
                                  text='API health checks',
                                  command=lambda: self._callback('btn_test'))

        self.btn_list_categories = tk.Button(master=self.frm_command,
                                             fg='blue',
                                             text='List categories',
                                             command=lambda: self._callback('btn_list_categories'))

        self.btn_activate_users = tk.Button(master=self.frm_command,
                                            fg='green',
                                            text='Create user(s)',
                                            command=lambda: self._callback('btn_activate_users'))

        self.btn_delete_users = tk.Button(master=self.frm_command,
                                          fg='red',
                                          text='Delete user(s)',
                                          command=lambda: self._callback('btn_delete_users'))

        self.btn_list_users = tk.Button(master=self.frm_command,
                                        fg='blue',
                                        text='List user(s)',
                                        command=lambda: self._callback('btn_list_users'))

        self.btn_ingest_accounts = tk.Button(master=self.frm_command,
                                             fg='green',
                                             text='Ingest account(s)',
                                             command=lambda: self._callback('btn_ingest_accounts'))

        self.btn_delete_accounts = tk.Button(master=self.frm_command,
                                             fg='red',
                                             text='Delete account(s)',
                                             command=lambda: self._callback('btn_delete_accounts'))

        self.btn_list_accounts = tk.Button(master=self.frm_command,
                                           fg='blue',
                                           text='List account(s)',
                                           command=lambda: self._callback('btn_list_accounts'))

        self.btn_ingest_trx = tk.Button(master=self.frm_command,
                                        fg='green',
                                        text='Ingest transaction(s)',
                                        command=lambda: self._callback('btn_ingest_trx'))

        self.btn_delete_trx = tk.Button(master=self.frm_command,
                                        fg='red',
                                        text='Delete transaction(s)',
                                        command=lambda: self._callback('btn_delete_trx'))

        self.btn_list_trx = tk.Button(master=self.frm_command,
                                      fg='blue',
                                      text='List transaction(s)',
                                      command=lambda: self._callback('btn_list_trx'))

        self.btn_process_all = tk.Button(master=self.frm_command,
                                         fg='brown',
                                         text='Process all steps',
                                         command=lambda: self._callback('btn_process_all'))

        self.btn_save_logs = tk.Button(master=self.frm_command,
                                       text='Save logs',
                                       command=lambda: self._callback('btn_save_logs'))

        self.btn_clear_logs = tk.Button(master=self.frm_command,
                                        text='Clear logs',
                                        command=lambda: self._callback('btn_clear_logs'))

        # --- Result Frame: Button Widgets

        dropdown_choices = list()
        for e in cfg.MessageDetailLevel:
            dropdown_choices.append(e.value)
        self.opt_msg_level_det_val.set(dropdown_choices[0])
        self.opt_msg_level_det = tk.OptionMenu(self.frm_result,
                                               self.opt_msg_level_det_val,
                                               *dropdown_choices,
                                               command=self._callback_option_button)

        # --- Result Frame: Text Widgets

        self.result_log = tkst.ScrolledText(
            master=self.frm_result,
            wrap=tk.WORD,
            width=cfg.UI_STRING_MAX_WITH,
            height=15,
            bg='beige')

    def _layout(self):
        """
        Setup the layout of the ui widgets using a grid layout.
        :return: Void.
        """
        # --- File Frame: Layout
        self.txt_usr_file_in.grid(row=1, column=2, sticky=tk.W)
        self.txt_acc_file_in.grid(row=2, column=2, sticky=tk.W)
        self.txt_trx_file_in.grid(row=3, column=2, sticky=tk.W)
        self.btn_usr_file_in.grid(row=1, column=3, sticky=tk.W)
        self.btn_acc_file_in.grid(row=2, column=3, sticky=tk.W)
        self.btn_trx_file_in.grid(row=3, column=3, sticky=tk.W)

        self.txt_usr_file_out.grid(row=1, column=4, sticky=tk.W)
        self.txt_acc_file_out.grid(row=2, column=4, sticky=tk.W)
        self.txt_trx_file_out.grid(row=3, column=4, sticky=tk.W)
        self.btn_usr_file_out.grid(row=1, column=5, sticky=tk.W)
        self.btn_acc_file_out.grid(row=2, column=5, sticky=tk.W)
        self.btn_trx_file_out.grid(row=3, column=5, sticky=tk.W)

        # --- Config Frame: Layout
        self.cbtn_delete.grid(row=1, column=1, sticky=tk.W)
        self.cbtn_result_file.grid(row=2, column=1, sticky=tk.W)

        self.cbtn_proxy.grid(row=1, column=2, sticky=tk.W)
        self.txt_proxy.grid(row=1, column=3, sticky=tk.W)

        # --- Command Frame Layout
        self.btn_test.grid(row=1, column=1, sticky=tk.W)
        self.btn_process_all.grid(row=1, column=2, columnspan=3, sticky=tk.SW)
        self.btn_delete_users.grid(row=2, column=1, sticky=tk.W)
        self.btn_delete_accounts.grid(row=2, column=2, sticky=tk.W)
        self.btn_delete_trx.grid(row=2, column=3, sticky=tk.W)
        self.btn_activate_users.grid(row=3, column=1, sticky=tk.W)
        self.btn_ingest_accounts.grid(row=3, column=2, sticky=tk.W)
        self.btn_ingest_trx.grid(row=3, column=3, sticky=tk.W)
        self.btn_list_users.grid(row=4, column=1, sticky=tk.W)
        self.btn_list_accounts.grid(row=4, column=2, sticky=tk.W)
        self.btn_list_trx.grid(row=4, column=3, sticky=tk.W)
        self.btn_list_categories.grid(row=4, column=4, sticky=tk.W)
        self.btn_clear_logs.grid(row=5, column=1, sticky=tk.W)
        self.btn_save_logs.grid(row=5, column=2, sticky=tk.W)

        # --- Result Frame Layout
        self.result_log.grid(row=1, column=1, sticky=tk.W)
        self.opt_msg_level_det.grid(row=2, column=1, sticky=tk.W)
    def _data_sync(self):
        """
        Synchronization of the data held in the ui components e.g. with the global
        configuration Singleton instance within config.TinkConfig.

        :return: void
        """
        cfg.TinkConfig.get_instance().user_source = self.txt_usr_file_in.get()
        cfg.TinkConfig.get_instance().account_source = self.txt_acc_file_in.get()
        cfg.TinkConfig.get_instance().transaction_source = self.txt_trx_file_in.get()

        cfg.TinkConfig.get_instance().user_target = self.txt_usr_file_out.get()
        cfg.TinkConfig.get_instance().account_target = self.txt_acc_file_out.get()
        cfg.TinkConfig.get_instance().transaction_target = self.txt_trx_file_out.get()

        cfg.TinkConfig.get_instance().delete_flag = self.cbtn_delete_val.get()
        cfg.TinkConfig.get_instance().proxy_flag = self.cbtn_proxy_val.get()
        cfg.TinkConfig.get_instance().result_file_flag = self.cbtn_result_file_val.get()
        cfg.TinkConfig.get_instance().message_detail_level = self.opt_msg_level_det_val.get()

    def _data_init(self):
        """
        Initialization of the UI components e.g. with default values.

        :return: Void.
        """
        file = cfg.IN_FILE_PATTERN_TINK.replace('*', 'Users')
        self.txt_usr_file_in.insert(0, file)
        self.txt_usr_file_out.insert(0, file.replace('In', 'Out'))

        file = cfg.IN_FILE_PATTERN_TINK.replace('*', 'Accounts')
        self.txt_acc_file_in.insert(0, file)
        self.txt_acc_file_out.insert(0, file.replace('In', 'Out'))

        file = cfg.IN_FILE_PATTERN_TINK.replace('*', 'Transactions')
        self.txt_trx_file_in.insert(0, file)
        self.txt_trx_file_out.insert(0, file.replace('In', 'Out'))

        # CheckButtons
        self.cbtn_delete.select()  # Pre-delete is enabled by default
        self.cbtn_result_file.select()  # Write results into a file by default
        self.cbtn_proxy.deselect()  # Proxy usage is disabled by default

        self.txt_proxy.config(state='normal')
        self.txt_proxy.insert(0, cfg.PROXY_URL + ':' + cfg.PROXY_PORT)
        self.txt_proxy.config(state='readonly')
        self._put_result_log(text=TinkUI.WELCOME_TEXT, nl=2, time=False)

    def _put_result_log(self, text: str, clear=False, nl: int = 1, time=True, scroll=False):
        """
        Write to the output (in the ui log area).

        :param text: The text to be displayed in the ui log area.
        :param clear: Flag indicating whether to clear the log before printing.
        :param nl: Number of newlines between the current text and the new text
        :param time: Flag indicating whether to show the time at the beginning of the line
        :param scroll: Flag indicating whether to scroll automatically with the text

        :return: Void
        """
        if clear:
            self._clear_result_log()

        if time:
            date_time = utl.strdate(datetime.datetime.now()) + ': '
        else:
            date_time = ''

        self.result_log.insert(tk.INSERT, date_time + text + os.linesep * nl)

        if scroll:
            self.result_log.see(tk.END)

        self.result_log.update()

    def _clear_result_log(self):
        """
        Clear the output (in the ui log area).
        :return: Void
        """
        self.result_log.delete(1.0, tk.END)

    def _run(self):
        """
        Main thread running the ui application in the main window.

        :return: void
        """
        self.window.mainloop()

    # --- Event Handler

    def _callback(self, code: str, event=None):
        """
        Generic action dispatcher that can be used for any kind of ui events.
        :param code: Unique action code which should be the name of the button.
        :return: Void.
        """
        logging.debug(f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}')
        logging.info(code)

        config = cfg.TinkConfig.get_instance()

        if not code:
            return
        # Checkbox Actions
        elif code == 'cbtn_result_file':
            config.result_file_flag = self.cbtn_result_file_val.get()
        elif code == 'cbtn_delete':
            config.delete_flag = self.cbtn_delete_val.get()
        elif code == 'cbtn_proxy':
            config.proxy_flag = self.cbtn_proxy_val.get()
        # Button Actions
        elif code == 'btn_usr_file_in':
            self.show_file_content(self.txt_usr_file_in.get())
        elif code == 'btn_usr_file_out':
            self.show_file_content(self.txt_usr_file_out.get())
        elif code == 'btn_acc_file_in':
            self.show_file_content(self.txt_acc_file_in.get())
        elif code == 'btn_acc_file_out':
            self.show_file_content(self.txt_acc_file_out.get())
        elif code == 'btn_trx_file_in':
            self.show_file_content(self.txt_trx_file_in.get())
        elif code == 'btn_trx_file_out':
            self.show_file_content(self.txt_trx_file_out.get())
        elif code == 'btn_test':
            self.call_model(action='API Health Checks',
                            method=self._model.test_connectivity)
        elif code == 'btn_activate_users':
            self.call_model(action='Create/Activate Users',
                            method=self._model.activate_users)
        elif code == 'btn_delete_users':
            self.call_model(action='Delete Users',
                            method=self._model.delete_users)
        elif code == 'btn_list_users':
            self.call_model(action='Get/List Users',
                            method=self._model.get_users)
        elif code == 'btn_ingest_accounts':
            self.call_model(action='Ingest Accounts',
                            method=self._model.ingest_accounts)
        elif code == 'btn_delete_accounts':
            self.call_model(action='Delete Accounts',
                            method=None)
        elif code == 'btn_list_accounts':
            self.call_model(action='Get/List Accounts',
                            method=self._model.get_all_accounts)
        elif code == 'btn_ingest_trx':
            self.call_model(action='Ingest Transactions',
                            method=None)
        elif code == 'btn_delete_trx':
            self.call_model(action='Delete Transactions',
                            method=None)
        elif code == 'btn_list_trx':
            self.call_model(action='Get/List Transactions',
                            method=None)
        elif code == 'btn_process_all':
            self.call_model_process_actions()
        elif code == 'btn_list_categories':
            # self.call_model(action='Get/List Categories',
            #                 method=self._model.list_categories)
            self._put_result_log(text='*** List categories ***',
                                 clear=True,
                                 time=False,
                                 nl=2)
            rl: model.TinkModelResultList = self._model.list_categories()
            r = rl.first()
            self._put_result_log(r.response.to_string_custom())

        elif code == 'btn_save_logs':
            utl.save_to_file(self.result_log.get(1.0, tk.END))
        elif code == 'btn_clear_logs':
            self._clear_result_log()

    def _callback_option_button(self, event=None):
        """
        Event Handler for events raised by an OptionButton.
        Hint: OptionButtons do slightly behave different to Buttons
        and CheckButtons. This is why the above generic event handler
        _callback cannot be used for these.

        :param event: Will contain the value of the OptionButton.
        :return: Void.
        """
        logging.debug(f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}')

        for enum_val in cfg.MessageDetailLevel:
            if enum_val.value == event:
                cfg.TinkConfig.get_instance().message_detail_level = enum_val

    def call_model(self, action: str, method, filters=None):
        """
        Generic method to call a method in the facade module model.
        :param action: A text describing the action performed. The chosen
        text will also be displayed on top of the ui result log.
        :param method: Reference to the method model.* that should be invoked.
        :param filters: dictionary with filters to be applied to the results
        :return: Void.
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        if not method:
            self._put_result_log(text=f'Action {action} is not yet implemented!',
                                 clear=True,
                                 time=False)
            return

        self._put_result_log(text=f'*** {action} ***',
                             clear=True,
                             time=False,
                             nl=2)
        logging.info(f'Action: {action} => Trying to dynamically invoke method {method}')

        rl: model.TinkModelResultList = None
        try:
            rl: model.TinkModelResultList = method()
        except Exception as e:
            error_text = f'Exception {type(e)}:\n{str(e)}'
            self._put_result_log(error_text)
            traceback.print_exc()

        if rl:
            filters = self._model.supported_action_filters(method)
            self._put_result_log(rl.summary(filters=filters))

    def call_model_process_actions(self):
        """
        Call all supported actions within the model facade.
        :return: Void.
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        action = 'Process all actions in one pipeline'
        self._put_result_log(text=f'*** {action} ***',
                             clear=True,
                             time=False,
                             nl=2)

        for action in self._model.process_actions:
            method = action['method']
            logging.info(f'Action: {action} => Trying to dynamically invoke method {method}')
            rl: model.TinkModelResultList = method()
            filters = self._model.supported_action_filters(method)
            self._put_result_log(rl.summary(filters=filters), nl=2)

    def show_file_content(self, filename):
        """
        Event Handler for the corresponding button cb_<method_name>

        :return: void
        """
        self._put_result_log(text=f'*** File content {filename} ***', clear=True, time=False)

        fh = utl.FileHandler()
        try:
            lst_data = fh.read_csv_file(filename=filename,
                                        skip_header=False)
            if data:
                text = utl.list_to_string(lst_data)
            else:
                text = 'No data available'
            self._put_result_log(text=text, time=False)
        except Exception as e:
            self._put_result_log(str(e))