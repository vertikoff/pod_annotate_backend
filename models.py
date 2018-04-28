from pymodm import fields, MongoModel


class NotedMedia(MongoModel):
    # because primary_key is True, we will need to query this
    # field using the label _id
    media_id = fields.CharField(primary_key=True)
    media_src = fields.URLField()
    media_title = fields.CharField()
    media_img = fields.URLField()
    # email = fields.EmailField()
    ts_start = fields.ListField(field=fields.FloatField())
    ts_end = fields.ListField(field=fields.FloatField())
    body = fields.ListField(field=fields.CharField())
    ts_insert = fields.ListField(field=fields.DateTimeField())
