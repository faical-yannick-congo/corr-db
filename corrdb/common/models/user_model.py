import datetime
from ..core import db
import json
import hashlib

# @TODO Issue with connected_at and datetime in general that makes it not stable in mongodb.
# Here i had to remove the msecondes from connected_at to make it stable from renew to allowance.
# I know it doesn't make sense. But it does the trick for now.
# This is a bug that i will have to fix later on for sure.

class UserModel(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.utcnow())
    connected_at = db.DateTimeField(default=datetime.datetime.utcnow())
    email = db.StringField(required=True, unique=True)
    api_token = db.StringField(max_length=256, unique=True)
    session = db.StringField(max_length=256, unique=True)
    possible_group = ["admin", "user", "developer", "public", "unknown"]
    group = db.StringField(default="unknown", choices=possible_group)
    extend = db.DictField()

    def __repr__(self):
        return '<User %r>' % (self.email)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def save(self, *args, **kwargs):
        if not self.api_token:
            self.api_token = hashlib.sha256(b'CoRRToken_%s'%(str(datetime.datetime.utcnow()))).hexdigest()

        if not self.session:
            self.session = hashlib.sha256(b'CoRRSession_%s'%(str(datetime.datetime.utcnow()))).hexdigest()

        return super(UserModel, self).save(*args, **kwargs)

    def renew(self, unic):
        self.connected_at = datetime.datetime.utcnow()
        self.session = hashlib.sha256(b'CoRRSession_%s_%s_%s'%(self.email, str(self.connected_at), unic)).hexdigest()
        self.save()

    def retoken(self):
        self.api_token = hashlib.sha256(b'CoRRToken_%s_%s'%(self.email, str(datetime.datetime.utcnow()))).hexdigest()
        self.save()

    def allowed(self, unic):
        return hashlib.sha256(b'CoRRSession_%s_%s_%s'%(self.email, str(self.connected_at).split('.')[0], unic)).hexdigest()

    def info(self):
        data = {'created':str(self.created_at), 'id': str(self.id), 'email' : self.email, 'group':self.group, 'total_projects' : len(self.projects), 'total_duration':self.duration, 'total_records':self.record_count}
        return data

    def extended(self):
        data = self.info()
        data['apiToken'] = self.api_token
        data['session'] = self.session
        data['extend'] = self.extend
        return data

    def to_json(self):
        data = self.extended()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    def activity_json(self, admin=False):
        projects_summary = [json.loads(p.summary_json()) for p in self.projects if not p.private or admin]
        return json.dumps({'user':self.extended(), 'projects' : projects_summary}, sort_keys=True, indent=4, separators=(',', ': '))

    @property
    def projects(self):
        from ..models import ProjectModel
        return ProjectModel.objects(owner=self)

    @property
    def records(self):
        records = []
        for project in self.projects:
            records += project.records
        return records

    @property
    def quota(self):
        #Add the filemodel to the quota check.
        from ..models import FileModel
        from ..models import EnvironmentModel
        occupation = 0
        for project in self.projects:
            for env in project.history:
                environment = EnvironmentModel.objects.with_id(env)
                occupation += environment.bundle['size']
            for record in project.records:
                for _file in FileModel.objects(record=record):
                    occupation += _file.size 
        return occupation
    
    @property
    def record_count(self):
        return sum([p.record_count for p in self.projects])

    @property
    def duration(self):
        try:
            return sum([p.duration for p in self.projects])
        except:
            return 0.0


            
