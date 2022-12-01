from sqlalchemy import (Column, Integer, String, DateTime, Enum, Table,
                        Boolean, ForeignKey)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from uniland.utils.enums import UserLevel, DocType

BASE = declarative_base()

bookmarks_association = Table(
    'bookmarks_association', BASE.metadata,
    Column('user_id', Integer,
           ForeignKey('users.user_id')),
    Column('submission_id', Integer,
           ForeignKey('submissions.id')))


# TODO! handle ON DELETE cascade in relationships
# When a user is deleted, not null constraint for submissions.owner_id
# will raise error
class User(BASE):
  __tablename__ = "users"
  
  user_id = Column(Integer, nullable=False, primary_key=True)  # user_id in telegram
  access_level = Column(Enum(UserLevel), nullable=False, default=UserLevel.Ordinary)
  last_step = Column(String(50), default='')

  # user_submissions : list -> one-to_many with Submission.owner

  # confirmations : list -> one-to-many with Submission.admin

  # many-to-many with Submission.liked_users
  bookmarks = relationship('Submission',
                           secondary=bookmarks_association,
                           back_populates='liked_users')

  def __init__(self, user_id, last_step=''):
    self.user_id = user_id
    self.last_step = last_step
    self.access_level = UserLevel.Ordinary

  def __repr__(self):
    return f'User {self.user_id} has access level {self.access_level}'

# ---------------------------------------------------------------------

class Submission(BASE):
  __tablename__ = "submissions"
  
  id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
  submission_date = Column(DateTime, default=datetime.utcnow)
  is_confirmed = Column(Boolean, default=False)

  # many-to-one with User.user_submissions
  owner_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
  owner = relationship('User', backref='user_submissions', foreign_keys=[owner_id])

  # many-to-one with User.confirmations
  admin_id = Column(Integer, ForeignKey('users.user_id'), default=None)
  admin = relationship('User', backref='confirmations', foreign_keys=[admin_id])

  # many-to-many with User.bookmarks
  liked_users = relationship('User',
                             secondary=bookmarks_association,
                             back_populates='bookmarks')

  university = Column(String(50))
  faculty = Column(String(30))
  search_text = Column(String(200))
  description = Column(String(500))

  submission_type = Column(String(20))

  __mapper_args__ = {
      "polymorphic_identity": "submission",
      "polymorphic_on": submission_type,
  }

  def __init__(self, 
              owner,
              is_confirmed=False, 
              correspondent_admin=None,
              university='نامشخص',
              faculty='نامشخص',
              search_text='',
              description='توضیحاتی برای این فایل ثبت نشده است.'):
    
    self.owner = owner
    self.is_confirmed = is_confirmed
    self.correspondent_admin = correspondent_admin
    self.university = university
    self.faculty = faculty
    self.search_text = search_text
    self.description = description

  def update_search_text(self):
    # This method is implemented in each subclass of Submission
    raise NotImplementedError("This method should not be called from Submission class")
  
  def confirm(self, user: User):
    if user == None or user.access_level.value <= 2: # 2 is Editor access
      raise RuntimeError("User doesn't have permission to confirm this submission")
    self.admin = user
    self.is_confirmed = True
    self.update_search_text()

# ---------------------------------------------------------------------

class Document(Submission):
  __tablename__ = "documents"
  
  id = Column(Integer, ForeignKey("submissions.id"), primary_key=True)
  file_id = Column(String(30), nullable=False, unique=True)
  unique_id = Column(String(30), nullable=False, unique=True)
  file_type = Column(Enum(DocType), nullable=False)  # Necessary field
  course = Column(String(30), nullable=False)  # Necessary field
  professor = Column(String(30), default='نامشخص')
  writer = Column(String(30), default='نامشخص')
  semester_year = Column(Integer, default=0)

  def __init__(self,
               owner,
               file_id,
               unique_id,
               is_confirmed=False,
               correspondent_admin=None,
               university='نامشخص',
               faculty='نامشخص',
               search_text='',
               description='توضیحاتی برای این فایل ثبت نشده است.',
               file_type=None,
               course='نامشخص',
               professor='نامشخص',
               writer='نامشخص',
               semester_year=0):
    
    self.owner = owner
    self.is_confirmed = is_confirmed
    self.correspondent_admin = correspondent_admin
    self.university = university
    self.faculty = faculty
    self.search_text = search_text
    self.description = description
    
    self.file_id = file_id
    self.unique_id = unique_id
    self.file_type = file_type
    self.course = course
    self.professor = professor
    self.writer = writer
    self.semester_year = semester_year
    
  def update_search_text(self):
    self.search_text = f'{self.file_type.value} درس {self.course}'
    if self.professor != 'نامشخص':
      self.search_text += f' استاد {self.professor}'
    if self.writer != 'نامشخص':
      self.search_text += f' نویسنده {self.writer}'
    if self.semester_year != 0:
      self.search_text += f' سال {self.semester_year}'
    if self.university != 'نامشخص':
      self.search_text += f' دانشگاه {self.university}'
    
  def __repr__(self):
    return f'Document {self.unique_id} from {self.owner}'

  __mapper_args__ = {
      "polymorphic_identity": "document",
  }

# ---------------------------------------------------------------------

class Profile(Submission):
  __tablename__ = "profiles"
  
  id = Column(Integer, ForeignKey("submissions.id"), primary_key=True)
  title = Column(String(200), nullable=False)
  email = Column(String(50), default='')
  phone_number = Column(String(25), default='')
  image_link = Column(String, default='')
  image_id = Column(String(30), default='')
  resume_link = Column(String, default='')
  resume_id = Column(String(30), default='')

  def __init__(self,
               owner,
               title='',
               email='',
               phone_number='',
               image_link='',
               image_id='',
               resume_link='',
               resume_id='',
               is_confirmed=False, 
               correspondent_admin=None,
               university='نامشخص',
               faculty='نامشخص',
               search_text='',
               description='توضیحاتی برای این فایل ثبت نشده است.'):
    
    self.is_confirmed = is_confirmed
    self.correspondent_admin = correspondent_admin
    self.university = university
    self.faculty = faculty
    self.search_text = search_text
    self.description = description
    
    self.owner = owner
    self.title = title
    self.email = email
    self.phone_number = phone_number
    self.image_link = image_link
    self.image_id = image_id
    self.resume_link = resume_link
    self.resume_id = resume_id
    
  def update_search_text(self):
    self.search_text = f'اطلاعات {self.title} دانشکده {self.faculty}'
    if self.faculty != 'نامشخص':
      self.search_text += f' دانشکده {self.faculty}'
    if self.university != 'نامشخص':
      self.search_text += f' دانشگاه {self.university}'
    
  def __repr__(self):
    return f'Profile {self.title} from {self.owner}'

  __mapper_args__ = {
      "polymorphic_identity": "profile",
  }

# ---------------------------------------------------------------------

class Media(Submission):
  __tablename__ = "medias"
  
  id = Column(Integer, ForeignKey("submissions.id"), primary_key=True)
  url = Column(String, nullable=False)
  media_type = Column(String(20), default=None)
  course = Column(String(30), nullable=False)  # Necessary field
  professor = Column(String(30), nullable=False)  # Necessary field
  semester_year = Column(Integer, default=0)

  def __init__(self, 
               owner, 
               url,
               media_type='',
               course='نامشخص',
               professor='نامشخص',
               semester_year=0,
               is_confirmed=False, 
               correspondent_admin=None,
               university='نامشخص',
               faculty='نامشخص',
               search_text='',
               description='توضیحاتی برای این فایل ثبت نشده است.'):
    self.owner = owner
    self.is_confirmed = is_confirmed
    self.correspondent_admin = correspondent_admin
    self.university = university
    self.faculty = faculty
    self.search_text = search_text
    self.description = description
    
    self.url = url
    self.media_type = media_type
    self.course = course
    self.professor = professor
    self.semester_year = semester_year
   
  def update_search_text(self):
    self.search_text = f'فیلم درس {self.course} استاد {self.professor}'
    if self.faculty != 'نامشخص':
      self.search_text += f' دانشکده {self.faculty}'
    if self.semester_year != 0:
      self.search_text += f' سال {self.semester_year}'
    if self.university != 'نامشخص':
      self.search_text += f' دانشگاه {self.university}'
    
  def __repr__(self):
    return f'Media {self.url} from {self.owner}'

  __mapper_args__ = {
      "polymorphic_identity": "media",
  }

def create_tables(engine):
  BASE.metadata.bind = engine
  BASE.metadata.create_all(engine, checkfirst=True)