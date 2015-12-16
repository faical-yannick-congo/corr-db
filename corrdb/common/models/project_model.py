import datetime
from ..core import db
from ..models import UserModel
from ..models import FileModel
from ..models import CommentModel
from ..models import EnvironmentModel
from ..models import ApplicationModel
import json
from bson import ObjectId
          
class ProjectModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow())
    application = db.ReferenceField(ApplicationModel)
    owner = db.ReferenceField(UserModel, reverse_delete_rule=db.CASCADE, required=True)
    name = db.StringField(required=True)
    description = db.StringField()
    goals = db.StringField()
    tags = db.ListField(db.StringField())
    possible_access = ["private", "protected", "public"]
    access = db.StringField(default="private", choices=possible_access)
    history = db.ListField(EnvironmentModel)
    cloned_from = db.StringField(max_length=256)
    resources = db.ListField(FileModel) #files ids
    possible_group = ["computational", "experimental", "hybrid", "undefined"]
    group = db.StringField(default="undefined", choices=possible_group)
    comments = db.ListField(CommentModel) #comments ids
    # TOREPLACE BY comments = db.ListField(db.StringField()) #comments ids
    extend = db.DictField()

    def clone(self):
        self.cloned_from = str(self.id)
        del self.__dict__['_id']
        del self.__dict__['_created']
        del self.__dict__['_changed_fields']
        self.id = ObjectId()

    def info(self):
        data = {'created':str(self.created_at), 'updated':str(self.last_updated), 'id': str(self.id), 
        'owner':str(self.owner.id), 'name': self.name, 'access':self.access, 'tags':len(self.tags), 
        'duration': str(self.duration), 'records':self.record_count, 'environments':len(self.history),
        'diffs':self.diff_count, 'comments':len(self.comments), 'resources':len(self.resources)}
        if self.application != None:
            data['application'] = str(self.application.id)
        else:
            data['application'] = None
        return data

    def extended(self):
        data = self.info()
        data['tags'] = self.tags
        data['goals'] = self.goals
        data['history'] = [env.extended() for env in self.history]
        data['description'] = self.description
        data['comments'] = [comment.extended() for comment in self.comments]
        data['resources'] = [resource.extended() for resource in self.resources]
        data['extend'] = self.extend
        return data

    def to_json(self):
        data = self.extended()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    def summary_json(self):
        data = self.info()
        data['tags'] = len(self.tags)
        if self.goals != None:
            data['goals'] = self.goals[0:96]+"..." if len(self.goals) >=100 else self.goals
        else:
            data['goals'] = None
        if self.description != None:
            data['description'] = self.description[0:96]+"..." if len(self.description) >=100 else self.description
        else:
            data['description'] = None
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    def activity_json(self, public=False):
        if not public:
            records_summary = [json.loads(r.summary_json()) for r in self.records]
            return json.dumps({'project':self.extended(), "records":records_summary}, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            if project.access == 'public':
                records_summary = []
                for record in self.records:
                    if record.access == 'public':
                        records_summary.append(json.loads(r.summary_json()))
                return json.dumps({'project':self.extended(), "records":records_summary}, sort_keys=True, indent=4, separators=(',', ': '))
            else:
                return json.dumps({}, sort_keys=True, indent=4, separators=(',', ': '))

    @property
    def record_count(self):
        return self.records.count()

    @property
    def diff_count(self):
        from ..models import DiffModel
        diffs = []
        for diff in DiffModel.objects():
            if diff.record_from.project == self:
                diffs.append(diff)
            if diff.record_to.project == self:
                diffs.append(diff)
        return len(diffs)
    @property
    def records(self):
        from ..models import RecordModel
        return RecordModel.objects(project=self).order_by('+created_at')
    
    @property
    def last_updated(self):
        if self.record_count >0:
            return self.records.order_by('-updated_at').limit(1).first().updated_at
        else:
            return self.created_at

    @property
    def duration(self):
        if self.records == None or len(self.records) == 0:
            return 0
        else:
            try:
                last_updated_strp = datetime.datetime.strptime(str(self.last_updated), '%Y-%m-%d %H:%M:%S.%f')
            except:
                last_updated_strp = datetime.datetime.strptime(str(self.last_updated), '%Y-%m-%d %H:%M:%S')

            try:
                created_strp = datetime.datetime.strptime(str(self.created_at), '%Y-%m-%d %H:%M:%S.%f')
            except:
                created_strp = datetime.datetime.strptime(str(self.created_at), '%Y-%m-%d %H:%M:%S')

            print str(last_updated_strp-created_strp)
            return last_updated_strp-created_strp