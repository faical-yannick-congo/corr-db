import datetime
from ..core import db
import json
import hashlib
from pytz import timezone
# datetime.utcnow()

class AccessModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow()) #datetime.datetime.now())
    possible_scope = ["api", "cloud", "root"]
    scope = db.StringField(default="root", choices=possible_scope)
    endpoint = db.StringField(max_length=256) #api/v1/push

    def __repr__(self):
        return '<Access %r>' % (self.created_at)

    def to_json(self):
        data = {}
        data['created_at'] = str(self.created_at)
        data['scope'] = self.scope
        data['endpoint'] = self.endpoint
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    def activity_json(self):
        data = {}
        #Build the statistics.
        data['api'] = {'total':len(AccessModel.object(scope='api')), 'endpoints':[]}
        data['api']['endpoints'] = AccessModel.object(scope='api').order_by('-endpoint')
        data['cloud'] = {'total':len(AccessModel.object(scope='cloud')), 'endpoints':[]}
        data['cloud']['endpoints'] = AccessModel.object(scope='cloud').order_by('-endpoint')
        
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))