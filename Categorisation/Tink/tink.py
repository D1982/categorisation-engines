""" Tink Application

"""

import Categorisation.Tink.ui as ui
import Categorisation.Tink.model as model
import Categorisation.Common.config as cfg

import logging


def main():
    # Initiate Logger
    logging.basicConfig(filename=cfg.TINK_LOGFILE, level=logging.DEBUG)
    app = ui.TinkUI(facade=model.TinkModel())
    app.run()


if __name__ == '__main__':
    main()
