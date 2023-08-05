from datetime import datetime, date

ALLOWED_EXTENSIONS = ['xls', 'xlsx']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def is_int(num):
    # print(num)
    # print(type(num))
    if isinstance(num, float):
        n = num * 10 % 10
        if n == 0.0:
            return True
        else:
            return False
    elif isinstance(num, int):
        return True
    else:
        return False


def excel_no(data=None):
    if isinstance(data, str):
        return data
    elif isinstance(data, float):
        return str(int(data))
    else:
        return None


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))
