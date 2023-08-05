from marshmallow import Schema, fields


class ExcleSchema(Schema):
    excel_id = fields.Integer()
    name = fields.String()
    import_time = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    status = fields.Integer()
