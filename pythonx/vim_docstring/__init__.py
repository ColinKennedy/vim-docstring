# IMPORT STANDARD LIBRARIES
import sys
import logging

LOGGER = logging.getLogger('vim_docstring')
_HANDLER = logging.StreamHandler(sys.stdout)
_FORMATTER = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
_HANDLER.setFormatter(_FORMATTER)
LOGGER.addHandler(_HANDLER)
