import datetime
from ..core import db
import json
from bson import ObjectId

from ..models import UserModel
from ..models import FileModel
          
class CommentModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow())
    sender = db.ReferenceField(UserModel, required=True)
    resource = db.ReferenceField(FileModel, reverse_delete_rule=db.CASCADE)
    title = db.StringField()
    content = db.StringField()
    attachments = db.ListField(FileModel) #files ids
    useful = db.ListField(UserModel)      #users ids
    extend = db.DictField()

    def clone(self):
        del self.__dict__['_id']
        del self.__dict__['_created']
        del self.__dict__['_changed_fields']
        self.id = ObjectId()

    def info(self):
        data = {'created':str(self.created_at), 'id': str(self.id), 'sender':str(self.sender.id), 'title':self.title,
        'content':self.content}
        if resource != None:
            data['resource'] = str(resource.id)
        data['useful'] = len(self.useful)
        data['attachments'] = len(self.attachments)
        return data

    def extended(self):
        data = self.info()
        if resource != None:
            data['resource'] = resource.extended()
        data['useful'] = []
        for us in useful:
            us_profile = ProfileModel.objects(user=us).first()
            if us_profile == None:
                data['useful'].append({'email_only':us.email})
            else:
                data['useful'].append(us_profile.info())
        data['attachments'] = [attachment.extended() for attachment in self.attachments]
        data['extend'] = self.extend
        return data

    def to_json(self):
        data = self.extended()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    def summary_json(self):
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))