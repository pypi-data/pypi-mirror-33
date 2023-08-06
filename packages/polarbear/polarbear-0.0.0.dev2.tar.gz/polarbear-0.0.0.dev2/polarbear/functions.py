import pandas as pd
from polarbear import entities


def convert_dataset_to_schema(ds, mapping, study):
    questions_info = mapping.info.drop(
        ['type_of_scale', 'scale_exists_in_database',
         'scale_name'], axis=1)
    scales_info = mapping.info[
        ['type_of_scale', 'scale_exists_in_database',
         'scale_id', 'scale_name']]

    questions_info = questions_info[questions_info['exists_in_database'] == 0]
    scales_info = scales_info[scales_info['scale_exists_in_database'] == 0]

    studies = pd.DataFrame(
        columns=['study_id', 'start_date', 'end_date', 'study_name'],
        data=[[study.study_id, study.start_date,
               study.end_date, study.study_name]])

    question_orders = pd.DataFrame({
        'study_id': study.study_id,
        'question_id': [dict(zip(mapping.info.question_id,
                        mapping.info.database_question_id)).get(
                        item, item) for item in list(ds.data.columns)],
        'order': [float(i) for i in (range(1, len(ds.data.columns) + 1))]
    })

    questions = pd.DataFrame({
        'question_id': questions_info.database_question_id,
        'full_text': questions_info.full_text,
        'display_text': questions_info.display_text,
        'category': questions_info.category,
        'subcategory': questions_info.subcategory,
        'topic': questions_info.topic,
        'subtopic': questions_info.subtopic,
        'type_of_response': questions_info.type_of_response,
        'scale_id': questions_info.scale_id
    })

    scales = pd.DataFrame({
        'scale_id': scales_info.scale_id,
        'scale_name': scales_info.scale_name,
        'type_of_scale': scales_info.type_of_scale
    })

    response_choices = pd.DataFrame({
        'question_id': ds.codebook.question_id.replace(
            dict(zip(mapping.info.question_id,
                     mapping.info.database_question_id))),
        'scale_id': ds.codebook.question_id.replace(
            dict(zip(mapping.info.question_id, mapping.info.scale_id))),
        'full_label': ds.codebook.full_label,
        'display_label': ds.codebook.display_label,
        'value': [float(i) for i in ds.codebook.value_code]
    })

    response_choices = response_choices[response_choices['question_id'].isin(
        questions_info.database_question_id)].copy().reset_index(drop=True)
    response_choices['response_choice_id'] = \
        response_choices.question_id.str.cat(
            response_choices.value.astype(int).astype(str), sep='_')

    closed_ended_mask = mapping.info.type_of_response.isin(
        ['Scale', 'Multiple response'])
    closed_ended_questions = list(mapping.info[closed_ended_mask].question_id)
    open_ended_questions = list(mapping.info[~closed_ended_mask].question_id)

    ds.data['id_in_study'] = ds.data['id_in_study'].astype(int).astype(str)
    ds.data['respondent_id'] = study.study_id + '_' + ds.data['id_in_study']

    closed_ended_data = ds.data[['respondent_id'] + closed_ended_questions]
    closed_ended_responses = pd.melt(
        closed_ended_data, id_vars='respondent_id', var_name='question_id')
    closed_ended_responses['question_id'].replace(
        dict(zip(mapping.info.question_id,
                 mapping.info.database_question_id)),
        inplace=True)
    closed_ended_responses.value = closed_ended_responses.value.astype(float)
    closed_ended_responses['study_id'] = study.study_id

    open_ended_data = ds.data[['respondent_id'] + open_ended_questions]
    open_ended_responses = pd.melt(
        open_ended_data, id_vars='respondent_id', var_name='question_id',
        value_name='text_response')
    open_ended_responses['question_id'].replace(
        dict(zip(mapping.info.question_id,
                 mapping.info.database_question_id)),
        inplace=True)
    open_ended_responses['study_id'] = study.study_id

    schemed = entities.Schema(
        studies, question_orders, questions, scales,
        response_choices, closed_ended_responses, open_ended_responses)

    return schemed
