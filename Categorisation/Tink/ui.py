"""UI components of the Tink client application."""

import Categorisation.Common.config as cfg
import Categorisation.Common.util as utl

import os
import sys
import logging

import tkinter as tk
import tkinter.scrolledtext as tkst

from tkinter import filedialog


class TinkUI:

    def __init__(self, facade):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        self._model = facade  # Linked model

        # --- Setup main window structure
        self.create_windows()
        self.create_frames()

        # --- Setup file frame
        self.setup_file_frame()

        # --- Setup config frame
        # Checkboxes need to be setup within the __init__ method since
        # otherwise callbacks will not work.

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

        # --- Setup command frame

        self.setup_command_frame()

        # --- Setup result frame
        self.setup_result_frame()

        # Button actions
        self.button_command_binding()

        # Default values
        self.ui_data()

        # Bind data in the model
        self.data_bindings()

    # --- Setup of the UI

    """Setup the main window."""
    def create_windows(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Widgets
        self.window = tk.Tk()
        self.window.title('Tink API Testing')

        # Layout
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

    """Setup the frames."""
    def create_frames(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

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

    """Setup the elements within the file frame."""
    def setup_file_frame(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Widgets
        self.label_file_patterns = tk.Label(self.file_frame, bg='lavender', text='File patterns:')
        self.label_file_in = tk.Label(self.file_frame, text='Input:')
        self.label_file_out = tk.Label(self.file_frame, text='Output:')

        self.label_files = tk.Label(self.file_frame, bg='lavender', text='Files:')
        self.label_file_users = tk.Label(self.file_frame, text='Input file Users:')
        self.label_file_accounts = tk.Label(self.file_frame, text='Input file Users:')
        self.label_file_trx = tk.Label(self.file_frame, text='Input file Users:')

        self.entry_file_out = tk.Entry(self.file_frame, width=30)
        self.entry_file_in = tk.Entry(self.file_frame, width=30)
        self.entry_user_file = tk.Entry(self.file_frame, width=40)
        self.entry_acc_file = tk.Entry(self.file_frame, width=40)
        self.entry_trx_file = tk.Entry(self.file_frame, width=40)

        self.show_userdata_button = tk.Button(self.file_frame, fg='violet', text='Show User Data')
        self.show_accdata_button = tk.Button(self.file_frame, fg='violet', text='Show Account Data')
        self.show_trxdata_button = tk.Button(self.file_frame, fg='violet', text='Show Trx Data')

        self.label_user_file = tk.Label(self.file_frame, text='User file:')
        self.label_account_file = tk.Label(self.file_frame, text='Account file:')
        self.label_trx_file = tk.Label(self.file_frame, text='Transaction file:')

        # Layout
        self.label_file_patterns.grid(row=0, column=1, padx=0, pady=5, sticky=tk.W)
        self.label_file_in.grid(row=1, column=1, sticky=tk.E)
        self.entry_file_in.grid(row=1, column=2, sticky=tk.W)

        self.label_file_out.grid(row=2, column=1, sticky=tk.E)
        self.entry_file_out.grid(row=2, column=2, sticky=tk.W)

        self.label_files.grid(row=3, column=1, padx=0, pady=5, sticky=tk.W)

        self.label_user_file.grid(row=4, column=1, sticky=tk.E)
        self.label_account_file.grid(row=5, column=1, sticky=tk.E)
        self.label_trx_file.grid(row=6, column=1, sticky=tk.E)

        self.entry_user_file.grid(row=4, column=2, sticky=tk.W)
        self.entry_acc_file.grid(row=5, column=2, sticky=tk.W)
        self.entry_trx_file.grid(row=6, column=2, sticky=tk.W)

        self.show_userdata_button.grid(row=4, column=3, sticky=tk.W)
        self.show_accdata_button.grid(row=5, column=3, sticky=tk.W)
        self.show_trxdata_button.grid(row=6, column=3, sticky=tk.W)

    """Setup the elements within the file frame. 
    
    This frame mainly consists of Checkbuttons that need to be bound to variables
    and callback methoeds. This does only work correctly if these elements are being 
    setup directly within the method __init__(), otherwise callbacks will not work.
    """
    def setup_config_frame(self):
        pass
        # This code  be found in __init__()

    """Setup the elements within the command frame."""
    def setup_command_frame(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Widgets
        self.label_commands = tk.Label(self.command_frame, bg='lavender', text='Commands:')
        self.test_button = tk.Button(self.command_frame, fg='blue', text='Test API connectivity')
        self.test_button = tk.Button(self.command_frame, fg='blue', text='Test API connectivity')
        self.auth_button = tk.Button(self.command_frame, fg='blue', text='Authorize client access')
        self.activate_users_button = tk.Button(self.command_frame, fg='blue', text='Create users')
        self.delete_users_button = tk.Button(self.command_frame, fg='blue', text='Delete users')

        # Layout
        self.label_commands.grid(row=0, column=1, padx=0, pady=10, sticky=tk.W)
        self.test_button.grid(row=1, column=1, sticky=tk.W)
        self.auth_button.grid(row=2, column=1, sticky=tk.W)
        self.activate_users_button.grid(row=3, column=1, sticky=tk.W)
        self.delete_users_button.grid(row=3, column=2, sticky=tk.W)

    """Setup the elements within the result frame."""
    def setup_result_frame(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Widgets
        self.label_results = tk.Label(self.result_frame, bg='lavender', text='Results:')
        # self.result_log = tk.Label(master=self.result_frame, anchor=tk.NW, justify=tk.LEFT)
        self.result_log = tkst.ScrolledText(
            master=self.result_frame,
            wrap=tk.WORD,
            width=cfg.UI_STRING_MAX_WITH,
            height=10,
            bg = 'beige'
        )
        self.save_button = tk.Button(self.result_frame, text='Save logs to file')
        self.clear_button = tk.Button(self.result_frame, text='Clear logs')

        # Layout
        self.label_results.grid(row=0, columnspan=2, padx=0, pady=10, sticky=tk.W)
        self.result_log.grid(row=1, columnspan=2, sticky=tk.NW)
        self.clear_button.grid(row=2, columnspan=2, sticky=tk.W)
        self.save_button.grid(row=3, columnspan=2, sticky=tk.W)

    """Initialization of the UI components e.g. with default data."""
    def ui_data(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        root_path = self.entry_file_in['text']
        in_pattern = cfg.IN_FILE_PATTERN_TINK
        out_pattern = cfg.OUT_FILE_PATTERN_TINK

        self.entry_file_in.insert(1, cfg.IN_FILE_PATTERN_TINK)
        self.entry_file_out.insert(1, cfg.OUT_FILE_PATTERN_TINK)

        # Set User file string
        text = self.entry_user_file
        text.config(state='normal')
        text.insert(0, root_path + in_pattern.replace('*', 'Users'))
        text.config(state='readonly')

        # Set Accounts file string
        text = self.entry_acc_file
        text.config(state='normal')
        text.insert(0, root_path + in_pattern.replace('*', 'Accounts'))
        text.config(state='readonly')

        # Set Transactions file string
        self.entry_trx_file.config(state='normal')
        self.entry_trx_file.insert(0, root_path + in_pattern.replace('*', 'Transactions'))
        self.entry_trx_file.config(state='readonly')

        # Checkbuttons
        self.chkbox_delete.deselect() # Pre-delete is enabled by default
        self.chkbox_proxy.deselect() # Proxy usage is disabled by default
        self.entry_proxy.config(state='normal')
        self.entry_proxy.insert(0, cfg.PROXY_URL + ':' + cfg.PROXY_PORT)
        self.entry_proxy.config(state='readonly')

    """Setup event handlers assigning actions to buttons."""
    def button_command_binding(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        self.show_userdata_button['command'] = self.button_show_userdata
        self.show_accdata_button['command'] = self.button_show_accdata
        self.show_trxdata_button['command'] = self.button_show_trxdata

        self.test_button['command'] = self.button_check_connectivity
        self.auth_button['command'] = self.button_authenticate
        self.activate_users_button['command'] = self.button_activate_users
        self.delete_users_button['command'] = self.button_delete_users

        self.clear_button['command'] = self.button_clear_log
        self.save_button['command'] = self.save_output_to_file

    """Main thread running the ui application in the main window."""
    def run(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        self.window.mainloop()

    # --- Event Handlers

    """Event Handler for button to display user data."""
    def button_show_userdata(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        self.clear_result_log()
        self.put_result_log('*** User data ***')
        result_list = self._model.read_user_data()

        if result_list:
            text = utl.list_to_string(result_list)
            self.put_result_log(text)

    """Event Handler for button to display account data."""
    def button_show_accdata(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        self.clear_result_log()
        self.put_result_log('*** Account data ***')
        result_list = self._model.read_account_data()

        if result_list:
            text = utl.list_to_string(result_list)
            self.put_result_log(text)

    """Event Handler for button to display transaction data."""
    def button_show_trxdata(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        self.clear_result_log()
        self.put_result_log('*** Transaction data ***')
        result_list = self._model.read_transaction_data()

        if result_list:
            text = utl.list_to_string(result_list)
            self.put_result_log(text)

    """Event Handler (Callback) for Checkbox 'Pre-delete'."""
    def chkbox_delete_cb(self, event=None):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        val = self.chkbox_delete_val.get()
        self._model.delete_flag = val
        print(self._model.delete_flag)


    """Event Handler (Callback) for Checkbox 'Use proxy'."""
    def chkbox_proxy_cb(self, event=None):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        val = self.chkbox_proxy_val.get()
        self._model.proxy_flag = val
        print(self._model.proxy_flag)


    """Event Handler for button to test the API connectivity."""
    def button_check_connectivity(self):
        result = self._model.test_connectivity()
        self.put_result_log(result)

    """Event Handler for button to authorize client access."""
    def button_authenticate(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        self.put_result_log('*** Authorize client access ***')
        result = self._model.authorize_client()
        self.put_result_log(result)

    """Event Handler for button to create a users."""
    def button_activate_users(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        self.put_result_log('*** Activate users ***')
        result = self._model.activate_users()
        self.put_result_log(result)

    """Event Handler for button to delete users."""
    def button_delete_users(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        self.put_result_log('*** Delete existing users ***')
        result = self._model.delete_users()
        self.put_result_log(result)

    """Event Handler for button to clear the output."""
    def button_clear_log(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        self.clear_result_log()

    """Event Handler for button to save the output into a file."""
    def save_output_to_file(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        type_list = [('Text files', '*.txt')]
        file_name = filedialog.asksaveasfilename(
            filetypes=type_list, defaultextension='*.txt'
        )
        # Save file if user entered a file name
        if file_name != '':
            with open(file_name, 'w') as output_file:
                output_file.writelines(self.result_log.get(1.0, tk.END))

    """Data bindings to provide required input data to the data access object.
    
    Currently the source data locations are solely files).
    """
    def data_bindings(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Provide required input data to the data access object (source data locations, here files)
        self._model.dao.bind_data_source(cfg.TinkEntityType.UserEntity, self.entry_user_file.get())
        self._model.dao.bind_data_source(cfg.TinkEntityType.AccountEntity, self.entry_acc_file.get())
        self._model.dao.bind_data_source(cfg.TinkEntityType.TransactionEntity, self.entry_trx_file.get())

    # --- Helpers

    """Write to the output."""
    def put_result_log(self, text):
        # self.result_log['text'] += os.linesep*2 + text
        self.result_log.insert(tk.INSERT, os.linesep*2 + text)
        self.result_log.see(tk.END)

    """Clear the output."""
    def clear_result_log(self):
        self.result_log.delete(1.0, tk.END)


