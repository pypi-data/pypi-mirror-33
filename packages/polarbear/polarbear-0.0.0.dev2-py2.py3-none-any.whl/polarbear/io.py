import pandas as pd
from polarbear import entities
from savReaderWriter import SavReader, SavHeaderReader
from sqlalchemy import and_, select, MetaData


def read_db(engine, study_ids):

    question_ids = get_question_ids_based_on_study_ids_from_db(engine, study_ids)
    question_metadata = read_question_metadata_from_db(
        engine, question_ids)
    codebook = read_codebook_from_db(engine, question_ids)
    data = read_data_from_db(engine, study_ids, question_ids,
                             question_metadata)

    ds = entities.Dataset(data, codebook, question_metadata)
    return ds


def get_question_ids_based_on_study_ids_from_db(engine, study_ids):

    conn = engine.connect()
    meta = MetaData(engine, reflect=True)

    question_orders = meta.tables['question_orders']
    s = select([question_orders.c.question_id]).where(
        question_orders.c.study_id.in_(study_ids))
    question_ids = list(pd.read_sql(s, conn).question_id)

    return question_ids


def read_question_metadata_from_db(engine, question_ids):
    conn = engine.connect()
    meta = MetaData(engine, reflect=True)

    questions = meta.tables['questions']
    s = select([questions]).where(questions.c.question_id.in_(question_ids))
    question_metadata = pd.read_sql(s, conn)
    scale_ids = list(question_metadata.scale_id.unique())

    scales = meta.tables['scales']
    s = select([scales]).where(scales.c.scale_id.in_(scale_ids))
    scale_metadata = pd.read_sql(s, conn)

    question_metadata = question_metadata.merge(
        scale_metadata, how='left', on=['scale_id'])

    return question_metadata


def read_codebook_from_db(engine, question_ids):
    conn = engine.connect()
    meta = MetaData(engine, reflect=True)

    response_choices = meta.tables['response_choices']
    s = select([response_choices]).where(
        response_choices.c.question_id.in_(question_ids))

    codebook = pd.read_sql(s, conn)[[
        'question_id', 'full_label', 'display_label', 'value']]

    codebook.rename(index=str, columns={'value': 'value_code'}, inplace=True)

    return codebook


def read_data_from_db(engine, study_ids, question_ids,
                      question_metadata=None):
    conn = engine.connect()
    meta = MetaData(engine, reflect=True)

    closed_ended_responses = meta.tables['closed_ended_responses']
    s = select([closed_ended_responses]).where((
        and_(closed_ended_responses.c.question_id.in_(question_ids),
             closed_ended_responses.c.study_id.in_(study_ids))))
    closed_ended_data = pd.read_sql(s, conn)
    closed_ended_data = closed_ended_data.pivot(
        index='respondent_id', columns='question_id', values='value')

    open_ended_responses = meta.tables['open_ended_responses']
    s = select([open_ended_responses]).where((
        and_(open_ended_responses.c.question_id.in_(question_ids),
             open_ended_responses.c.study_id.in_(study_ids))))
    open_ended_data = pd.read_sql(s, conn)
    open_ended_data = open_ended_data.pivot(
        index='respondent_id', columns='question_id', values='text_response')

    data = closed_ended_data.merge(
        open_ended_data, how='left', left_index=True, right_index=True)

    data.reset_index(inplace=True)

    if question_metadata is None:
        question_metadata = read_question_metadata_from_db(
            engine, question_ids)

    for i, row in question_metadata.iterrows():
        if row['type_of_response'] == 'Date':
            data[row['question_id']] = pd.to_datetime(data[row['question_id']])

    return data


def _handle_read_spss_datetime(data, datetime_cols=None,
                               date_cols=None, time_cols=None):

    if datetime_cols is not None:
        for col in datetime_cols:
            data[col] = pd.to_datetime(
                data[col]-7456579200, unit='s',
                origin=pd.to_datetime('1819-01-28'))

    if date_cols is not None:
        for col in date_cols:
            data[col] = pd.to_datetime(
                data[col]-7456579200, unit='s',
                origin=pd.to_datetime('1819-01-28')).dt.date

    if time_cols is not None:
        for col in time_cols:
            data[col] = pd.to_datetime(data[col], unit='s').dt.time

    return data


def read_spss(filepath, ioUtf8=True, datetime_cols=None,
              date_cols=None, time_cols=None, *args, **kwargs):

    with SavReader(filepath, ioUtf8=ioUtf8, *args, **kwargs) as reader:
        cols = reader.header
        d = reader.all()
    data = pd.DataFrame(columns=cols, data=d).replace(
        ['\r', '\n'], '', regex=True)

    if not ((datetime_cols is None) & (date_cols is None) &
            (time_cols is None)):
        data = _handle_read_spss_datetime(data,
                                          datetime_cols=datetime_cols,
                                          date_cols=date_cols,
                                          time_cols=time_cols)

    with SavHeaderReader(filepath, ioUtf8=ioUtf8) as header:
        var_names = [v for v in header.all().varNames]
        var_labels = ({k: v for
                       k, v in header.all().varLabels.items()})
        value_labels = header.all().valueLabels
        value_labels = [[[question,
                          value,
                          label]
                        for value, label in value_label_map.items()] for
                        question, value_label_map in value_labels.items()]
        value_labels = [value_label_map for question in value_labels
                        for value_label_map in question]
        codebook = pd.DataFrame(columns=['question_id', 'value_code',
                                         'full_label'],
                                data=value_labels)
        codebook['display_label'] = codebook.full_label
        m = pd.DataFrame(
            columns=['question_id', 'full_text', 'display_text',
                     'category', 'subcategory', 'topic', 'subtopic',
                     'type_of_response',
                     'scale_id', 'scale_name', 'type_of_scale']
        )
        m.question_id = var_names
        m.full_text = m.question_id.replace(var_labels)
        question_metadata = m.replace(['\r', '\n'], '', regex=True)

    ds = entities.Dataset(data, codebook, question_metadata)
    return ds


def read_csv(filepath, codebook_path=None,
             question_metadata_path=None, *args, **kwargs):
    data = pd.read_csv(filepath, *args, **kwargs)

    if codebook_path is not None:
        codebook = pd.read_csv(codebook_path, *args, **kwargs)
    else:
        codebook = None

    if question_metadata_path is not None:
        question_metadata = pd.read_csv(
            question_metadata_path, *args, **kwargs)
    else:
        question_metadata = None

    ds = entities.Dataset(data, codebook, question_metadata)
    return ds


def read_schema_from_csv(schema_studies_filepath,
                         schema_question_orders_filepath,
                         schema_questions_filepath,
                         schema_scales_filepath,
                         schema_response_choices_filepath,
                         schema_closed_ended_responses_filepath,
                         schema_open_ended_responses_filepath
                         ):
    studies = pd.read_csv(schema_studies_filepath)
    studies['start_date'] = pd.to_datetime(studies['start_date'])
    studies['end_date'] = pd.to_datetime(studies['end_date'])

    question_orders = pd.read_csv(schema_question_orders_filepath)
    question_orders['order'] = question_orders['order'].astype(float)

    questions = pd.read_csv(schema_questions_filepath)
    scales = pd.read_csv(schema_scales_filepath)

    response_choices = pd.read_csv(schema_response_choices_filepath)
    response_choices['value'] = response_choices['value'].astype(float)

    closed_ended_responses = pd.read_csv(
        schema_closed_ended_responses_filepath)
    closed_ended_responses['value'] = closed_ended_responses['value'].astype(float)

    open_ended_responses = pd.read_csv(schema_open_ended_responses_filepath)

    schema = entities.Schema(
        studies, question_orders, questions, scales,
        response_choices, closed_ended_responses, open_ended_responses)

    return schema
