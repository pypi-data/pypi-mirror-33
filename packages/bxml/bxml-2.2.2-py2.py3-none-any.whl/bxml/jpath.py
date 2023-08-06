"""jpath: Similar to xpath, works on dicts created with XML.as_dict()
/ separates nodes by one level
// separates nodes by multiple levels
"""

import re
from copy import deepcopy

def jpath(path, data):
    path_vals = re.split(r'(/+)', path)
    