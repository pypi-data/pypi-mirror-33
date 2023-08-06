import logging
import re
import string
import uuid
from difflib import SequenceMatcher

from django.utils import timezone

LOGGER = logging.getLogger("utility")


def get_current_datetime():
    """
    Returns the current timestamp taking the timezone into consideration
    """
    return timezone.now()

def get_uuid1():
    """
    Returns a new uuidv1
    """
    return uuid.uuid1()

def get_zero_uuid():
    """
    Returns a uuid containing only 0s
    """
    zero_uuid = uuid.UUID('00000000000000000000000000000000')
    LOGGER.debug(zero_uuid)
    return zero_uuid

def str_to_uuid1(value):
    """
    Converts the given string value into a uuid
    """
    return uuid.UUID(value)

def is_email_valid(email):
    """
    Checks if the given email address is valid
    """
    reg_ex = r"[^@]+@[^@]+\.[^@]+"
    if re.match(reg_ex, email):
        return True

    return False

def are_similar(value_a, value_b):
    """
    Returns the degree of similarity of the two string values a and b
    """
    sim = SequenceMatcher(None, value_a.lower(), value_b.lower()).ratio()
    return sim

def contains_char_classes(value, noc):
    """
    Checks if the given string value contains noc or more classes of characters,
    those classes are: upper case and lower case letters, digits and special
    characters
    """
    found = 0

    if any(c in value for c in string.ascii_lowercase):
        found += 1
    if any(c in value for c in string.ascii_uppercase):
        found += 1
    if any(c in value for c in string.digits):
        found += 1
    if any(c in value for c in string.punctuation):
        found += 1

    if found >= noc:
        return True

    return False

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    """
    Checks if two floating point numbers are almost equal
    """
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)