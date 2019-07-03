"""The entry point to initiate the Tink client application."""

import Categorisation.Tink.ui as ui
import Categorisation.Tink.model as model
import Categorisation.Tink.data as data
import Categorisation.Common.config as cfg

import logging


"""Main function starting the Tink client application."""


def main():

    # Initiate Logger
    logging.basicConfig(filename=cfg.TINK_LOGFILE, level=logging.DEBUG)

    # Create data access object
    dao = data.TinkDAO()

    # Create model facade and connect it with the data access object
    facade = model.TinkModel(dao=dao)

    # Create the user interface and connect it with the model facade
    app = ui.TinkUI(facade=facade)

    # Start the user interface (Tkinter)
    app.run()


"""Tink client application Entry Point"""
if __name__ == '__main__':
    main()
