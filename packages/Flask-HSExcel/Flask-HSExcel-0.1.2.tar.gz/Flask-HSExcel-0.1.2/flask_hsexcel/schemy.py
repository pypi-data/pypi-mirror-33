from marshmallow import Schema, fields


class ExcleSchema(Schema):
    excel_id = fields.Integer()
    name = fields.String()
    import_time = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    status = fields.Integer()
    excel_type = fields.String()
    extend = fields.String()

class BaseSchema(Schema):
    # 自定义Schema
    def _str(self, data=None):
        if isinstance(data, str):
            return data
        elif isinstance(data, float):
            return str(int(data))
        else:
            return None

    def list_to_str(self, data=None):
        if data:
            return str(data)


class StyleSchema(BaseSchema):
    item = fields.Method(deserialize="_str", attribute='size_code')
    model = fields.Method(deserialize="_str", attribute='color_code')
    iman = fields.Method(deserialize="_str", attribute='style_code')
    color = fields.Method(deserialize="_str", attribute='color_name')
    scale = fields.Method(deserialize="_str", attribute='size_name')
    seq = fields.Method(deserialize="_str", attribute='order')
    pcb = fields.Integer(attribute='per_box_case')
    ue = fields.Integer(attribute='per_tape_case')
    box = fields.Method(deserialize="_str", attribute='box_spec')
    season = fields.Method(deserialize="_str", attribute='season_name')
    brand = fields.Method(deserialize="_str", attribute='brand_name')
    error = fields.Method(deserialize="list_to_str")


class MaterialSchema(BaseSchema):
    materialname = fields.Method(deserialize="_str", attribute='material_name')  # 物种名称
    mmodelcode = fields.Method(deserialize="_str", attribute='material_code')  # 物种编码
    stockunit = fields.Method(deserialize="_str", attribute='stock_unit')  # 库存单位
    pruchaseunit = fields.Method(deserialize="_str", attribute='pr_unit')  # 采购单位
    rate = fields.Float(attribute='unit_stock2pr_rate')  # 采购库存转换率
    specification = fields.Method(deserialize="_str", attribute='spec')  # 规格型号
    component = fields.Method(deserialize="_str", attribute='component')  # 成分
    gmwidth = fields.Method(deserialize="_str", attribute='grey_fabric_width')  # 坯布幅宽
    gmm = fields.Method(deserialize="_str", attribute='grey_fabric_weight')  # 坯布克重
    fpwidth = fields.Method(deserialize="_str", attribute='finish_product_width')  # 成品幅宽
    fpm = fields.Method(deserialize="_str", attribute='finish_product_weight')  # 成品克重
    scale = fields.Method(deserialize="_str", attribute='scale')  # 辅料第一规格
    secondscale = fields.Method(deserialize="_str", attribute='second_scale')  # 辅料第二规格
    mcolorname = fields.Method(deserialize="_str", attribute='material_item_name')  # 颜色名称
    mcolorenname = fields.Method(deserialize="_str", attribute='material_item_en_name')
    mcolorcode = fields.Method(deserialize="_str", attribute='material_item_code')  # 色号，颜色编码(相同物料下唯一)
    mitemcode = fields.Method(deserialize="_str", attribute='material_item_no')  # 物料编码(全局唯一)


class InventorySchema(Schema):
    material_item_no = fields.String()  # 物料编码(model)
    material_item_code = fields.String()  # 物料色号(item)
    material_item_spec = fields.String()  # 物料描述
    production_line = fields.String()  # 生产线
    storage_quantity = fields.Number(as_string=True)  # 在库数
    unit_name = fields.String()  # 单位
    remark = fields.String()  # 备注
    error = fields.String()
    excel_id = fields.String()


class InventoryStyleSchema(Schema):
    style_code = fields.String()  # 款号
    color_code = fields.String()  # 色号(model编码)
    size_group_code = fields.String()  # 尺码组编码
    size_item_code = fields.String()  # 尺码编码
    storage_quantity = fields.Number(as_string=True)  # 在库数
    size_name = fields.String()  # 尺码名称
    # remark = fields.String()
    error = fields.String()
    excel_id = fields.String()


class BomSchema(Schema):
    pass
