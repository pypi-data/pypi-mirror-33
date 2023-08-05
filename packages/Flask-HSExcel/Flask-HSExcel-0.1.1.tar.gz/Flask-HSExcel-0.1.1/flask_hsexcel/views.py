import os, time, random, logging
from flask import current_app, jsonify, Blueprint, request, send_file, make_response
from .utils import allowed_file
from .schemy import ExcleSchema

hs_excel = Blueprint('hs_excel', __name__)

logger = logging.getLogger(__name__)


@hs_excel.route('/import/', methods=['POST', 'GET', 'DELETE'])
def get_excel():
    """获得excel,并对excel进行基础的格式校验"""
    from .models import get_session, ExcelModel
    from .task import check_error
    excel_type = request.args.get('excel_type')
    db_session = get_session()
    if not excel_type:
        return jsonify({'message': '请拼接excel_type'}), 400
    if request.method == 'POST':
        base_path = current_app.config.get('EXCEL_PATH')
        import_path = os.path.join(base_path, 'import')
        error_path = os.path.join(base_path,'error')
        file = request.files['file']
        if not (file and allowed_file(filename=file.filename)):
            return jsonify({'message': 'excel格式不正确,文件上传失败'}), 400

        # 这里有个方法要对excel进行基础校验，主要是看看能不能解析出来
        time_str = str(time.time())
        random_str = str(random.randint(1, 10000))
        if file.filename.split('.')[1] == 'xls':
            file_save_name = time_str + random_str + '.xls'
        else:
            file_save_name = time_str + random_str + '.xlsx'
        file_path = os.path.join(import_path, file_save_name)
        file.save(file_path)
        excel = ExcelModel()
        excel.name = file.filename
        excel.path = file_path
        excel.excel_type = excel_type
        db_session.add(excel)
        db_session.flush()
        ## 这个地方放异步任务
        check_error.delay(excel.excel_id, excel_type,error_path)
        schema = ExcleSchema(many=False)
        result = schema.dump(excel).data
        return jsonify(result)
    # 获取上传的所有excel的列表，导入时间倒序排序，带分页
    elif request.method == 'GET':
        page = request.args.get('page', 1)
        per_page = request.args.get('per_page', 10)
        query = db_session.query(ExcelModel).filter(ExcelModel.excel_type == excel_type).order_by(
            ExcelModel.import_time)
        paginate = query.paginate(page=int(page), per_page=per_page)
        items = paginate.items
        total = paginate.total
        schema = ExcleSchema(many=True)
        data = schema.dump(items).data
        result = {'data': data,
                  'paging': {'page': int(page),
                             'per_page': int(per_page),
                             'total_number': int(total)}}
        # print(1111111111)
        return jsonify(result)

    else:
        excel_ids = request.get_json().get('excel_ids')
        excels = db_session.query(ExcelModel).filter(ExcelModel.excel_id.in_(excel_ids)).all()
        for excel in excels:
            path = excel.path
            error_path = excel.error_path
            try:
                os.remove(path)
                os.remove(error_path)
            except Exception as e:
                logger.error(e)
        db_session.flush()
        return jsonify(None), 204


@hs_excel.route('/one/excel/', methods=['GET'])
def get_one_excel():
    """获取单个上传的excel"""
    excel_id = request.args.get('excel_id')
    if not excel_id:
        return jsonify({'message': 'excel_id必传'}), 400
    from .models import get_session, ExcelModel
    db_session = get_session()
    excel = db_session.query(ExcelModel).filter(ExcelModel.excel_id == excel_id).first()
    path = excel.path
    file_name = excel.name
    file = send_file(path)
    response = make_response(file)
    response.headers["Content-Disposition"] = "attachment; filename={}".format(file_name.encode().decode('latin-1'))
    return response


@hs_excel.route('/error/export/', methods=['GET'])
def get_error_excel():
    """下载带错误的excel文件"""
    excel_id = request.args.get('excel_id')
    if not excel_id:
        return jsonify({'message': 'excel_id必传'}), 400
    from .models import get_session, ExcelModel
    db_session = get_session()
    excel = db_session.query(ExcelModel).filter(ExcelModel.excel_id == excel_id).first()
    path = excel.error_path
    file_name = excel.name
    file = send_file(path)
    response = make_response(file)
    response.headers["Content-Disposition"] = "attachment; filename={}".format(file_name.encode().decode('latin-1'))
    return response
