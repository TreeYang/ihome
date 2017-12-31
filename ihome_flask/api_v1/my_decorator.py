from flask import session, jsonify
from status_code import *

import functools
def is_login(view_fun):
    @functools.wraps(view_fun)
    def inner(*args, **kwargs):
        if 'user_id' in session:
            return view_fun(*args,**kwargs)
        else:
            return jsonify(RET.LOGINERR)
    return inner