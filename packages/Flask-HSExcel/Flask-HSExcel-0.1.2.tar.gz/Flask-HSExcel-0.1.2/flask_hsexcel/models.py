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
    excel的处理状态
    status 状态
    extend 拼接参数的传递
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
    extend = db.Column(db.String(256), nullable=True)


class MaterialTemporary(db.Model):
    # 物料临时表
    __tablename__ = 'material_temporary'

    material_id = db.Column(db.Integer, primary_key=True)
    excel_id = db.Column(db.Integer, nullable=True)
    material_name = db.Column(db.NVARCHAR(500), nullable=True, default="")  # 物种名称
    material_code = db.Column(db.NVARCHAR(500), nullable=True, default="")  # 物种编码
    stock_unit = db.Column(db.NVARCHAR(50), nullable=True, default="")  # 库存单位
    pr_unit = db.Column(db.NVARCHAR(50), nullable=True, default="")  # 采购单位
    unit_stock2pr_rate = db.Column(db.DECIMAL(9, 4), nullable=True, default=1.00)  # 采购库存转换率
    spec = db.Column(db.NVARCHAR(50), nullable=True, default="")  # 规格型号
    error = db.Column(db.Integer, default=0)
