import datetime
from ..core import db
import json
from bson import ObjectId
          
class EnvironmentModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow())
    possible_group = ["computational", "experimental", "hybrid", "unknown"]
    group = db.StringField(default="unknown", choices=possible_group)
    possible_system = ["container-based", "vm-based", "tool-based", "cloud-based", "device-based", "lab-based", "custom-based", "undefined"]
    system = db.StringField(default="undefined", choices=possible_system)
    specifics = db.DictField() # {'container-system':'docker|rocket', 'container-version':'1.0'}, {'tool-system':'guilogger', 'tool-version':'1.0'} # {'profile-version':'python-script', 'profile-version':'python 2.7'}
    version = db.DictField() #{'system':'git|hg|svn', branch':'branch_name', commit':'tag', 'timestamp':''}
    bundle = db.DictField() #{'scope':'local|remote', 'location':'hash|https://container.host.com/id', 'size':0}

    def clone(self):
        del self.__dict__['_id']
        del self.__dict__['_created']
        del self.__dict__['_changed_fields']
        self.id = ObjectId()

    def info(self):
        data = {'created':str(self.created_at), 'id': str(self.id), 'group':self.group,
        'system':self.system, 'specifics':self.specifics, 'version': self.version, 'bundle':self.bundle}
        return data

    def to_json(self):
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))