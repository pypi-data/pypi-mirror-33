from app import hsexcel
from app import checker
from .checker import ErrorChecker

celery = hsexcel.make_celery()


def get_checker(excel_type):
    return checker.get(excel_type, ErrorChecker)


@celery.task
def check_error(id=None, param=None, error_path=None):
    excel_type = param.get('excel_type')[0]
    Checker = get_checker(excel_type)
    checker = Checker(id, error_path, param)
    checker.as_json()
    checker.add_error()
    return 'success'
