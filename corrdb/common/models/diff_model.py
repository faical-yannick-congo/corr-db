import datetime
from ..core import db
from ..models import UserModel
from ..models import RecordModel
import json
from bson import ObjectId
          
class DiffModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow())
    sender = db.ReferenceField(UserModel, reverse_delete_rule=db.CASCADE, required=True)
    targeted = db.ReferenceField(UserModel, reverse_delete_rule=db.CASCADE, required=True)
    record_from = db.ReferenceField(RecordModel, reverse_delete_rule=db.CASCADE, required=True)
    record_to = db.ReferenceField(RecordModel, reverse_delete_rule=db.CASCADE, required=True)
    # diff = db.DictField() #{'method':'default|visual|custom', 'specific1':'', ...}
    possible_method = ["default", "visual", "custom", "undefined"]
    method = db.StringField(default="undefined", choices=possible_method)
    resources = db.ListField(db.StringField()) # List of files ids that are used to justify the diff
    possible_proposition = ["repeated", "reproduced", "replicated", "non-replicated", "non-repeated", "non-reproduced", "undefined"]
    proposition = db.StringField(default="undefined", choices=possible_proposition)
    possible_status = ["proposed", "agreed", "denied", "undefined", "altered"]
    status = db.StringField(default="undefined", choices=possible_status)
    comments = db.ListField() #{"user":str(user_id), "created":str(datetime.datetime.utc()), "title":"", "content":""}

    def clone(self):
        del self.__dict__['_id']
        del self.__dict__['_created']
        del self.__dict__['_changed_fields']
        self.id = ObjectId()

    def info(self):
        data = {'created':str(self.created_at), 'id': str(self.id), 
        'from':str(self.record_from.id), 'to': str(self.record_to.id), 'proposition':self.proposition, 
        'method': self.method, 'status': self.status}
        return data

    def to_json(self):
        data = self.info()
        data['sender'] = str(self.sender.id)
        data['targeted'] = str(self.targeted.id)
        # data['diff'] = self.diff
        data['comments'] = self.comments
        data['resources'] = self.resources
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    def summary_json(self):
        data = self.info()
        data['comments'] = len(self.comments)
        data['resources'] = len(self.resources)
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))