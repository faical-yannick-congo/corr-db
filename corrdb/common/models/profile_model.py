import datetime
from ..core import db
from ..models import UserModel
import json
from bson import ObjectId
          
class ProfileModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow())
    user = db.ReferenceField(UserModel, reverse_delete_rule=db.CASCADE, required=True)
    fname = db.StringField(max_length=300, required=True)
    lname = db.StringField(max_length=300, required=True)
    picture = db.DictField() # {'scope':'local|remote', 'location':'hash|https://hoster.host.com/id'}
    organisation = db.StringField(max_length=500)
    about = db.StringField(max_length=1000)

    def clone(self):
        del self.__dict__['_id']
        del self.__dict__['_created']
        del self.__dict__['_changed_fields']
        self.id = ObjectId()

    def info(self):
        data = {'created':str(self.created_at), 'id': str(self.id), 
        'user':str(self.user.id), 'fname': self.fname, 'lname': self.lname, 'picture':self.picture}
        # data['status'] = self.status
        return data

    def to_json(self):
        data = self.info()
        data['organisation'] = self.organisation
        data['about'] = self.about
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    def summary_json(self):
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
