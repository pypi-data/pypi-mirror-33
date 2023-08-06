from sqlalchemy import Column, Date, Float, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Study(Base):
    __tablename__ = 'studies'

    study_id = Column(String(10), primary_key=True)
    study_name = Column(String(255), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)

    def __init__(self, study_id, study_name, start_date, end_date):
        self.study_id = study_id
        self.study_name = study_name
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self):
        return "<Study(study_id = '%s', study_name='%s', start_date='%s', end_date='%s')>" % (
            self.study_id, self.study_name, self.start_date, self.end_date)


class QuestionOrder(Base):
    __tablename__ = 'question_orders'

    study_id = Column(
        String(10), ForeignKey('studies.study_id'), primary_key=True)
    question_id = Column(
        String(50), ForeignKey('questions.question_id'), primary_key=True)
    order = Column(Float)

    question = relationship("Question")
    study = relationship("Study")

    def __init__(self, study_id, question_id, order):
        self.study_id = study_id
        self.question_id = question_id
        self.order = order


class Scale(Base):
    __tablename__ = 'scales'

    scale_id = Column(String(50), primary_key=True)
    scale_name = Column(String(50))
    type_of_scale = Column(String(50))

    def __init__(self, scale_id, scale_name, type_of_scale):
        self.scale_id = scale_id
        self.scale_name = scale_name
        self.type_of_scale = type_of_scale


class Question(Base):
    __tablename__ = 'questions'

    question_id = Column(String(50), primary_key=True)
    full_text = Column(String)
    display_text = Column(String(50))
    category = Column(String(50))
    subcategory = Column(String(50))
    topic = Column(String(50))
    subtopic = Column(String(50))
    type_of_response = Column(String(50))
    scale_id = Column(String(10), ForeignKey('scales.scale_id'))

    scale = relationship("Scale")

    def __init__(self, question_id, full_text, display_text,
                 category, subcategory, topic, subtopic,
                 type_of_response, scale_id):
        self.question_id = question_id
        self.full_text = full_text
        self.display_text = display_text
        self.category = category
        self.subcategory = subcategory
        self.topic = topic
        self.subtopic = subtopic
        self.type_of_response = type_of_response
        self.scale_id = scale_id


class ResponseChoice(Base):
    __tablename__ = 'response_choices'

    response_choice_id = Column(String(50), primary_key=True)
    question_id = Column(String(50), ForeignKey('questions.question_id'))
    scale_id = Column(String(10), ForeignKey('scales.scale_id'))
    full_label = Column(String(50))
    display_label = Column(String(50))
    value = Column(Float)

    scale = relationship("Scale")
    question = relationship("Question")

    def __init__(self, response_choice_id, question_id, scale_id,
                 full_label, display_label, value):
        self.response_choice_id = response_choice_id
        self.question_id = question_id
        self.scale_id = scale_id
        self.full_label = full_label
        self.display_label = display_label
        self.value = value


class ClosedEndedResponse(Base):
    __tablename__ = 'closed_ended_responses'

    study_id = Column(
        String(10), ForeignKey('studies.study_id'), primary_key=True)
    respondent_id = Column(
        String(50), primary_key=True)
    question_id = Column(
        String(50), ForeignKey('questions.question_id'), primary_key=True)
    value = Column(Float)

    question = relationship("Question")
    study = relationship("Study")

    def __init__(self, study_id, respondent_id, question_id,
                 value):
        self.study_id = study_id
        self.respondent_id = respondent_id
        self.question_id = question_id
        self.value = value


class OpenEndedResponse(Base):
    __tablename__ = 'open_ended_responses'

    study_id = Column(
        String(10), ForeignKey('studies.study_id'), primary_key=True)
    respondent_id = Column(
        String(50), primary_key=True)
    question_id = Column(
        String(50), ForeignKey('questions.question_id'), primary_key=True)
    text_response = Column(String)

    question = relationship("Question")
    study = relationship("Study")

    def __init__(self, study_id, respondent_id, question_id,
                 text_response):
        self.study_id = study_id
        self.respondent_id = respondent_id
        self.question_id = question_id
        self.text_response = text_response
