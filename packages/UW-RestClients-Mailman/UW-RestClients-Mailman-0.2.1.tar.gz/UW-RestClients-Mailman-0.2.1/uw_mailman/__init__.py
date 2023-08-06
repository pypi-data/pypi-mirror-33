"""
This is the interface for interacting with the mailman web service.
"""

import logging
from uw_mailman.dao import Mailman_DAO
from restclients_core.exceptions import DataFailureException


logger = logging.getLogger(__name__)


def get_resource(url):
    response = Mailman_DAO().getURL(url, {'Accept': 'application/json'})
    logger.info("GET %s ==status==> %s" % (url, response.status))

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    logger.debug("GET %s ==data==> %s" % (url, response.data))
    return response.data
