import re,os,time,random,xlrd,xlutils.copy,json,openpyxl,shutil
from .utils import is_int,json_serial


class ErrorChecker(object):
    config = [
    ]

    def __init__(self, id, error_path):
        from .models import get_session, ExcelModel
        db_session = get_session()
        self.db_session = db_session
        excel = db_session.query(ExcelModel).filter(ExcelModel.excel_id == id).first()
        self.excel = excel
        self.error_path = error_path

    def check(self, row_dict, index):
        configs = self.config
        error_list = []
        for config in configs:
            method = config[1]
            error = self.__getattribute__(method)(config[0], config[2], row_dict, index)
            if error:
                error_list.append(error)
        return error_list

    def check_int(self, name, error_str, row_dict, index):
        num = row_dict.get(name)
        if is_int(num):
            return None
        return '第{index}行{name}{error_str}'.format(index=index, name=name, error_str=error_str)

    def as_json(self):
        """考虑xls和xlsx的不同"""
        path = self.excel.path
        # print(path)
        if path.split('.')[2] == 'xls':
            excel_open = xlrd.open_workbook(path)
            table = excel_open.sheet_by_index(0)
            rows = table.nrows
            old_excel_title = table.row_values(0)
            excel_title = []
            for title in old_excel_title:
                real_title = re.sub(r'\s', '', title).lower()
                excel_title.append(real_title)
            json_list = []
            for i in range(2, rows):
                row_dict = dict(zip(excel_title, table.row_values(i)))
                row_dict['error'] = self.check(row_dict, i + 1)
                json_list.append(row_dict)
        else:
            excel_open = openpyxl.load_workbook(path)
            sheets = excel_open.sheetnames
            sheet0 = sheets[0]
            table = excel_open[sheet0]
            rows = table.rows
            # print(next(rows))
            old_excel_title = [col.value for col in list(rows)[0]]
            excel_title = []
            for title in old_excel_title:
                real_title = re.sub(r'\s', '', title).lower()
                excel_title.append(real_title)
            json_list = []
            i = 0
            rows = table.rows
            for row in rows:
                i = i + 1
                if i <= 2:
                    continue
                row_value = [col.value for col in row]
                row_dict = dict(zip(excel_title, row_value))  # []
                row_dict['error'] = self.check(row_dict, i)
                json_list.append(row_dict)

        json_str = json.dumps(json_list,default=json_serial,ensure_ascii=False)
        self.excel.content = json_str
        self.excel.status = 1
        self.db_session.flush()

    def add_error(self):
        path = self.excel.path
        time_str = str(time.time())
        random_str = str(random.randint(1, 10000))
        if path.split('.')[2] == 'xls':
            file_save_name = time_str + random_str + '.xls'
            real_path = os.path.join(self.error_path, file_save_name)
            shutil.copyfile(path, real_path)
            rb = xlrd.open_workbook(real_path, formatting_info=True)
            wb = xlutils.copy.copy(rb)
            sheet = rb.sheet_by_index(0)
            cols = sheet.ncols
            write_sheet = wb.get_sheet(0)
            write_sheet.write(0, cols , 'ERROR')
            contents = json.loads(self.excel.content)
            for i, content in enumerate(contents):
                write_sheet.write(i + 2, cols , str(content.get('error'))[1:-1])
        else:
            file_save_name = time_str + random_str + '.xlsx'
            real_path = os.path.join(self.error_path, file_save_name)
            shutil.copyfile(path, real_path)
            wb = openpyxl.load_workbook(real_path)
            sheets = wb.sheetnames
            sheet0 = sheets[0]
            table = wb[sheet0]
            cols = len(list(table.columns))
            table.cell(row=1, column=cols+1).value = 'Error'
            contents = json.loads(self.excel.content)
            for i, content in enumerate(contents):
                table.cell(row=i + 3, column=cols+1).value = str(content.get('error'))[1:-1]
        wb.save(real_path)
        self.excel.error_path = real_path
        self.excel.status = 2
        self.db_session.flush()
