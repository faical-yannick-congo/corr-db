from ..core import db
import datetime
import json
from bson import ObjectId

class FileModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow())
    encoding = db.StringField()
    mimetype = db.StringField()
    size = db.LongField()
    name = db.StringField()
    path = db.StringField()
    storage = db.StringField()
    possible_location = ["local", "remote", "undefined"]
    location = db.StringField(default="undefined", choices=possible_location)
    possible_group = ["input", "output", "dependencie", "descriptive", "diff", "attach", "picture" , "logo" , "resource", "undefined"]
    group = db.StringField(default="undefined", choices=possible_group)
    description = db.StringField()
    extend = db.DictField()

    def info(self):
        data = {'created_at':str(self.created_at), 'id': str(self.id), 
        'name':self.name, 'encoding':self.encoding, 'mimetype': self.mimetype, 'size': self.size, 'path': self.path, 'location':self.location}
        return data

    def extended(self):
        data = self.info()
        data['path'] = self.path
        data['storage'] = self.storage
        data['group'] = self.group
        data['description'] = self.description
        data['extend'] = self.extend
        return data

    def to_json(self):
        data = self.extended()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    def summary_json(self):
        data = self.info()
        data['comments'] = len(self.comments)
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))