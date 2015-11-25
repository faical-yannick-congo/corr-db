from ..core import db
# from ..models import RecordModel
# from ..models import ProjectModel
# from ..models import DiffModel
import datetime
import json
from bson import ObjectId

class FileModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow())
    # record = db.ReferenceField(RecordModel, reverse_delete_rule=db.CASCADE)#, required=True)
    # project = db.ReferenceField(ProjectModel, reverse_delete_rule=db.CASCADE)#, required=True)
    # diff = db.ReferenceField(DiffModel, reverse_delete_rule=db.CASCADE)#, required=True)
    encoding = db.StringField(max_length=50)
    mimetype = db.StringField(max_length=50)
    size = db.LongField()
    name = db.StringField()
    relative_path = db.StringField()
    location = db.StringField()
    possible_group = ["input", "output", "dependencies", "descriptive", "diff", "undefined"]
    group = db.StringField(default="undefined", choices=possible_group)
    description = db.StringField(max_length=512)
    comments = db.ListField() #{"user":str(user_id), "created":str(datetime.datetime.utc()), "title":"", "content":""}

    def info(self):
        data = {'created_at':str(self.created_at), 'id': str(self.id), 
        'name':self.name, 'encoding':self.encoding, 'mimetype': self.mimetype, 'size': self.size}
        # 'record':None, 'project':None, 'name':self.name, 'diff':None, 'encoding':self.encoding,
        # if self.record != None:
        #     data['record'] = self.record.id
        # if self.project != None:
        #     data['project'] = self.project.id

        return data

    def to_json(self):
        data = self.info()
        data['relative_path'] = self.relative_path
        data['location'] = self.location
        data['group'] = self.group
        data['description'] = self.description
        data['comments'] = self.comments)
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    def summary_json(self):
        data = self.info()
        data['comments'] = len(self.comments)
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))