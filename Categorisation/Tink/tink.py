""" Tink Application

"""

import Categorisation.Tink.ui as ui
import Categorisation.Tink.model as model
import Categorisation.Tink.data as data
import Categorisation.Common.config as cfg

import logging


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


if __name__ == '__main__':
    main()
