""" Tink Model

"""
import Categorisation.Tink.model as model
import Categorisation.Tink.api as api

import Categorisation.Common.config as cfg

import tkinter as tk
import easygui as gui
import logging

from tkinter import filedialog


class TinkUI:

    def __init__(self, facade):
        # Linked model
        self.model = facade

        # Setup main window structure
        self.create_windows()
        self.create_frames()

        # Setup frames
        self.setup_file_frame()
        self.setup_config_frame()
        self.setup_command_frame()
        self.setup_result_frame()

        # Button actions
        self.button_command_binding()

        # Default values
        self.ui_data()

    def create_windows(self):
        # --- Widgets
        self.window = tk.Tk()
        self.window.title('Tink API Testing')

        # --- Layout
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

    def create_frames(self):
        # --- Widgets
        self.header_frame = tk.Frame(master=self.window, padx=5, pady=5)
        self.file_frame = tk.Frame(master=self.window, padx=5, pady=5)
        self.config_frame = tk.Frame(master=self.window, padx=5, pady=5)
        self.command_frame = tk.Frame(master=self.window, padx=5, pady=5)
        self.result_frame = tk.Frame(master=self.window, padx=5, pady=5)

        # --- Layout
        self.file_frame.grid(row=1, sticky=tk.NW)
        self.config_frame.grid(row=2, sticky=tk.NW)
        self.command_frame.grid(row=3, sticky=tk.NW)
        self.result_frame.grid(row=4, sticky=tk.NW)

    def setup_file_frame(self):
        # --- Widgets
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
        self.entry_account_file = tk.Entry(self.file_frame, width=40)
        self.entry_trx_file = tk.Entry(self.file_frame, width=40)

        self.label_user_file = tk.Label(self.file_frame, text='User file:')
        self.label_account_file = tk.Label(self.file_frame, text='Account file:')
        self.label_trx_file = tk.Label(self.file_frame, text='Transaction file:')

        # --- Layout
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
        self.entry_account_file.grid(row=5, column=2, sticky=tk.W)
        self.entry_trx_file.grid(row=6, column=2, sticky=tk.W)

    def setup_config_frame(self):

        # --- Widgets
        self.label_config = tk.Label(self.config_frame, bg='lavender', text='Configuration:')
        self.chkbox_nohttp = tk.Checkbutton(self.config_frame, text='Suppress http calls')
        self.chkbox_proxy = tk.Checkbutton(self.config_frame, text='Use a proxy server')
        self.entry_proxy = tk.Entry(self.config_frame, width=30)

        # --- Layout
        self.label_config.grid(row=0, column=1, padx=0, pady=10, sticky=tk.W)
        self.chkbox_nohttp.grid(row=1, column=1, sticky=tk.W)
        self.chkbox_proxy.grid(row=2, column=1, sticky=tk.W)
        self.entry_proxy.grid(row=2, column=2, sticky=tk.W)

    def setup_command_frame(self):
        # --- Widgets
        self.label_commands = tk.Label(self.command_frame, bg='lavender', text='Commands:')
        self.test_button = tk.Button(self.command_frame, fg='blue', text='Test API connectivity')
        self.test_button = tk.Button(self.command_frame, fg='blue', text='Test API connectivity')
        self.auth_button = tk.Button(self.command_frame, fg='blue', text='Authorize client access')

        # --- Layout
        self.label_commands.grid(row=0, column=1, padx=0, pady=10, sticky=tk.W)
        self.test_button.grid(row=1, column=1, sticky=tk.W)
        self.auth_button.grid(row=2, column=1, sticky=tk.W)


    def setup_result_frame(self):

        # --- Widgets
        self.label_results = tk.Label(self.result_frame, bg='lavender', text='Results:')
        self.result_log = tk.Label(master=self.result_frame)
        self.save_button = tk.Button(self.result_frame, text='Save to file')
        self.clear_button = tk.Button(self.result_frame, text='Clear')

        # --- Layout
        self.label_results.grid(row=0, column=1, padx=0, pady=10, sticky=tk.W)
        self.clear_button.grid(row=1, column=1, sticky=tk.W)
        self.save_button.grid(row=1, column=2, sticky=tk.W)
        self.result_log.grid(row=2, column=2, sticky=tk.W)



    def put_result_log(self, text):
        self.result_log['text'] = text

    def print_result_log(self, text):
        # Place the resulting logs into the label
        self.put_result_log(text)


    def ui_data(self):
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
        text = self.entry_account_file
        text.config(state='normal')
        text.insert(0, root_path + in_pattern.replace('*', 'Accounts'))
        text.config(state='readonly')

        # Set Transactions file string
        text = self.entry_trx_file
        text.config(state='normal')
        text.insert(0, root_path + in_pattern.replace('*', 'Transactions'))
        text.config(state='readonly')

        # Set Proxy string
        text = self.entry_proxy
        text.config(state='normal')
        text.insert(0, cfg.PROXY_URL + ':' + cfg.PROXY_PORT)
        text.config(state='readonly')

    def button_check_connectivity(self):
        result = self.model.test_connectivity()
        self.print_result_log(result)

    def button_authenticate(self):
        result = self.model.authentication()
        self.print_result_log(result['message'])

    def button_clear_log(self):
        self.put_result_log('')

    def save_output_to_file(self):
        '''Save the output box into a text file'''
        type_list = [('Text files', '*.txt')]
        file_name = filedialog.asksaveasfilename(
            filetypes=type_list, defaultextension='*.txt'
        )
        # Save file if user entered a file name
        if file_name != '':
            with open(file_name, 'w') as output_file:
                output_file.writelines(self.result_log['text'])

    # Assign the commands to the buttons
    def button_command_binding(self):
        self.test_button['command'] = self.button_check_connectivity
        self.auth_button['command'] = self.button_authenticate

        self.clear_button['command'] = self.button_clear_log
        self.save_button['command'] = self.save_output_to_file

    def run(self):
        # Start the application
        self.window.mainloop()

