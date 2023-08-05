from datetime import datetime
from app import db


def get_session():
    return db.create_scoped_session(options={
        'autoflush': False,
        'autocommit': True
    })


class ExcelModel(db.Model):
    """
    excel_id : 主键
    name: 名称
    path: 路径
    content: 内容,text,包含error
    error_path: 包含错误的excel下载地址
    import_time: 导入时间
    """
    __tablename__ = 'hs_excel'

    excel_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(128), nullable=True)
    path = db.Column(db.String(256), nullable=True)
    excel_type = db.Column(db.String(50), nullable=True)
    content = db.Column(db.Text, nullable=True)
    error_path = db.Column(db.String(256), nullable=True)
    import_time = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(db.Integer, default=0)
