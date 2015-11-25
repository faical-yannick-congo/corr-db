from ..core import db
import datetime
import json
from bson import ObjectId
# (traffic, created) = TrafficModel.objects.get_or_create(service="", endpoint="")
class TrafficModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow(), required=True)
    service = db.StringField() #api, cloud for now
    endpoint = db.StringField() #account/...
    interactions = db.LongField(default=0)

    def info(self):
        data = {'created':str(self.created_at), 'id': str(self.id), 
        'service':str(self.service)}
        return data

    def to_json(self):
        data = self.info()
        data['interactions'] = self.interactions
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    def summary_json(self):
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))