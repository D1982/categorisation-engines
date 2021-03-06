"""The entry point to initiate the Tink client application."""

import Categorisation.Tink.ui as ui
import Categorisation.Tink.model as model
import Categorisation.Tink.data as data
import Categorisation.Common.config as cfg

import logging


def main():
    """
    Main function starting the Tink client application.
    :return: void
    """
    # Initiate Logger
    logging.basicConfig(filename=cfg.TINK_LOGFILE, level=cfg.LOG_LEVEL)

    # Create data access object
    dao = data.TinkDAO(data_provider=cfg.DataProviderType.File)

    # Create model facade and connect it with the data access object
    facade = model.TinkModel(dao=dao)

    # Create the user interface and connect it with the model facade
    app = ui.TinkUI(model_facade=facade)

    # Start the user interface (Tkinter)
    app._run()


"""Tink client application Entry Point"""
if __name__ == '__main__':
    main()
