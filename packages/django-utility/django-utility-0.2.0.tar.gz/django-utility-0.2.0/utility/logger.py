import logging

from utility.functions import get_current_datetime

LOGGER = logging.getLogger("utility")


def get_log_msg(req, user):
    """
    Returns a log string that contains common data available through views
    """
    data = req.data.copy()
    if 'password' in data:
        data['password'] = '************'
        LOGGER.debug(repr(data))

    templ = "{0}: METHOD: {1}; PATH_INFO: {2}; REMOTE_ADDR: {3}; \
            HTTP_USER_AGENT: {4}; DATA: {5}; USER_ID: {6}"

    msg = templ.format(get_current_datetime(),
                       req.META['req_METHOD'] if 'req_METHOD' in req.META else 'N/A',
                       req.META['PATH_INFO'] if 'PATH_INFO' in req.META else 'N/A',
                       req.META['REMOTE_ADDR'] if 'REMOTE_ADDR' in req.META else 'N/A',
                       req.META['HTTP_USER_AGENT'] if 'HTTP_USER_AGENT' in req.META else 'N/A',
                       data,
                       user.id if user is not None else 'N/A')
    return msg
