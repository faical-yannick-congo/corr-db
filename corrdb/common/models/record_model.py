from ..core import db
from ..models import ProjectModel
from ..models import EnvironmentModel
import datetime
import json
from bson import ObjectId

class RecordModel(db.Document):
    project = db.ReferenceField(ProjectModel, reverse_delete_rule=db.CASCADE, required=True)
    parent = db.ReferenceField(RecordModel, reverse_delete_rule=db.CASCADE)
    label = db.StringField(max_length=300)
    tags = db.ListField(db.StringField())
    created_at = db.DateTimeField(default=datetime.datetime.utcnow())
    updated_at = db.DateTimeField(default=datetime.datetime.utcnow())
    system = db.DictField() # {''} add os version, gpu infos, compiler infos.
    # will not be in the head anymore. And will be called executable instead of program 
    # Because we will also have experiment. They will all be in body
    # program = db.DictField() # {'version_control':'git|hg|svn|cvs', 'scope':'local|remote', 'location':'hash|https://remote_version.com/repository_id'}
    inputs = db.ListField(db.DictField()) # [{}]
    outputs = db.ListField(db.DictField()) # [{}]
    dependencies = db.ListField(db.DictField())# [{}]
    possible_status = ["starting", "started", "paused", "sleeping", "finished", "crashed", "aborded", "resumed", "running", "unknown"]
    status = db.StringField(default="unknown", choices=possible_status)
    environment = db.ReferenceField(EnvironmentModel, reverse_delete_rule=db.CASCADE)
    cloned_from = db.StringField(max_length=256)
    possible_access = ["private", "protected", "public"]
    access = db.StringField(default="private", choices=possible_access)
    resources = db.ListField(db.StringField()) # List of files ids
    # private = db.BooleanField(default=True)
    # protected = db.BooleanField(default=True)
    rationels = db.ListField(db.StringField()) #Why did you do this record. What is different from others.
    comments = db.ListField(db.DictField()) #{"user":str(user_id), "created":str(datetime.datetime.utc()), "title":"", "content":""}

    def clone(self):
        self.cloned_from = str(self.id)
        del self.__dict__['_id']
        del self.__dict__['_created']
        del self.__dict__['_changed_fields']
        self.id = ObjectId()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        return super(RecordModel, self).save(*args, **kwargs)
    
    def update_fields(self, data):
        for k, v in self._fields.iteritems():
            if not v.required:
                if k != 'created_at':
                        yield k, v
    
    def update(self, data):
        for k, v in self.update_fields(data):
            if k in data.keys():
                if k == 'created_at':
                    #self.created_at = datetime.datetime.strptime(data[k], '%Y-%m-%d %X')
                    pass
                else:
                    setattr(self, k, data[k])
                del data[k]
        self.save() 
        # print str(data)       
        if data:
            body, created = RecordBodyModel.objects.get_or_create(head=self)
            body.data.update(data)
            body.save()

    @property
    def files(self):
        from ..models import FileModel
        return FileModel.objects(record=self).order_by('+created_at')

    @property
    def body(self):
        return RecordBodyModel.objects(head=self).first()

    @property
    def duration(self):
        try:
            updated_strp = datetime.datetime.strptime(str(self.updated_at), '%Y-%m-%d %H:%M:%S.%f')
        except:
            updated_strp = datetime.datetime.strptime(str(self.updated_at), '%Y-%m-%d %H:%M:%S')

        try:
            created_strp = datetime.datetime.strptime(str(self.created_at), '%Y-%m-%d %H:%M:%S.%f')
        except:
            created_strp = datetime.datetime.strptime(str(self.created_at), '%Y-%m-%d %H:%M:%S')

        print str(updated_strp-created_strp)
        return updated_strp-created_strp

    def info(self):
        data = {'updated':str(self.updated_at),
         'id': str(self.id), 'project':str(self.project.id), 
         'label': self.label, 'created':str(self.created_at), 'status' : self.status, 'access':self.access}
        return data

    def to_json(self):
        data = {}
        data['head'] = self.info()
        # data['head']['program'] = self.program
        if self.parent != None:
            data['head']['parent'] = str(self.parent.id)
        else:
            data['head']['parent'] = None
        data['head']['tags'] = self.tags
        data['head']['system'] = self.system
        data['head']['inputs'] = self.inputs
        data['head']['outputs'] = self.outputs
        data['head']['dependencies'] = self.dependencies
        data['head']['comments'] = self.comments
        data['head']['resources'] = self.resources
        data['head']['rationels'] = self.rationels
        if self.body:
            data['body'] = self.body.info()
        if self.environment:
            data['environment'] = self.environment.info()
        else:
            data['environment'] = {}
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    def summary_json(self):
        data = self.info()
        data['tags'] = len(self.tags)
        data['inputs'] = len(self.inputs)
        data['outputs'] = len(self.outputs)
        data['dependencies'] = len(self.dependencies)
        data['comments'] = len(self.comments)
        data['resources'] = len(self.resources)
        data['rationels'] = len(self.rationels)
        if self.environment:
            data["environment"] = True
        else:
            data['environment'] = False
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

class RecordBodyModel(db.Document):
    updated_at = db.DateTimeField(default=datetime.datetime.utcnow())
    head = db.ReferenceField(RecordModel, reverse_delete_rule=db.CASCADE, unique=True)
    data = db.DictField()

    def info(self):
        data = {'updated':str(self.updated_at), 'id':str(self.id), 'content':self.data['data']}
        return data

    def to_json(self):
        data = {}
        data['body'] = self.info()
        data['head'] = json.loads(self.head.info())
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    def summary_json(self):
        data = {}
        data['body'] = self.info()
        data['head'] = json.loads(self.head.summary_json())
        # print "Data: "+str(data)
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))


        

