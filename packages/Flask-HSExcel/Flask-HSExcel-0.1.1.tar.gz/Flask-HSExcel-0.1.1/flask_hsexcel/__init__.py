import sys,os, logging
from .views import hs_excel
from celery import Celery
from .checker import ErrorChecker
logger = logging.getLogger(__name__)


class HsExcel(object):

    def __init__(self, app=None, checker=None):
        if app is not None:
            self.app = app
            self.checker = checker
            # self.db = db
            self.init_app(self.app, self.checker)
        else:
            self.app = None
            # self.db = None

    def init_app(self, app, checker):
        self.app = app
        self.checker = checker
        excel_path = self.app.config.get('EXCEL_PATH')
        # 判断是否传入　excelpath
        if not excel_path:
            logger.error("EXCEL_PATH没有配置")
            sys.exit(0)
        # 判断checker是否正确
        if not isinstance(self.checker, dict):
            logger.error('checker不是一个dict')
            sys.exit(0)
        if isinstance(self.checker, dict):
            for value in self.checker.values():
                if not isinstance(value,type):
                    logger.error('checker配置错误')
                    sys.exit(0)
                if not issubclass(value,ErrorChecker):
                    logger.error('checker配置不正确')
                    sys.exit(0)
        import_path = os.path.join(excel_path, 'import')
        error_path = os.path.join(excel_path, 'error')
        for _dir in [excel_path, import_path, error_path]:
            if not os.path.exists(_dir):
                os.mkdir(_dir)
        # 注册路由
        self.app.register_blueprint(hs_excel, url_prefix='/hs_excel')

    def make_celery(self):
        celery = Celery(self.app.import_name, broker=self.app.config['CELERY_BROKER_URL'])
        celery.conf.update(self.app.config)
        return celery

    def print_test(self):

        # print('hhhh')
        return '这是插件里面的内容'
