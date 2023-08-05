import datetime
import os

GITLAB_TOKEN_ENV = 'GITLAB_TOKEN'


def check_token(token):
    if token is None:
        try:
            token = os.environ[GITLAB_TOKEN_ENV]
        except KeyError as e:
            print("KeyError - Environment variable :{} containing your gitlab token could not be found".format(e))

    return token


def get_name_and_id(project_dict):
    project_info = []
    for elem in project_dict:
        project_info.append({'id': elem['id'], 'name': elem['name']})

    return project_info


def get_pipelines_id(pipeline_dict):
    pipelines = []
    for elem in pipeline_dict:
        pipelines.append(elem['id'])

    return pipelines


def get_pipeline_info(elem):
    pipeline_info = {'id': elem['id'],
                     'status': elem['status'],
                     'duration': elem['duration'],
                     'date': str(elem['finished_at'])[:10]
                     }
    return pipeline_info


def seconds_to_min(seconds):
    min, sec = divmod(round(seconds), 60)
    return "{} min {}s".format(round(min), sec)


def get_duration_moy(project_info):
    duration = 0
    for pipeline in project_info['pipelines']:
        duration += pipeline['duration']

    return duration / len(project_info['pipelines'])


def get_success_percentage(project_info):
    success = 0
    for pipeline in project_info['pipelines']:
        if pipeline['status'] is 'success':
            success += 1

    return round(success * 100 / len(project_info['pipelines']))


def get_pipeline_info_from(project_info, days=15):
    date = datetime.datetime.now() - datetime.timedelta(days=days)
    pipelines = []
    for pipeline in project_info['pipelines']:
        if datetime.datetime.strptime(pipeline['date'], "%Y-%m-%d") > date:
            pipelines.append(pipeline)
        else:
            break
    project_info['pipelines'] = pipelines

    return project_info


def enhance_project_info(project_info):
    project_info.update({"duration_moy": get_duration_moy(project_info)})
    project_info.update({"duration_in_minutes": seconds_to_min(project_info['duration_moy'])})
    project_info.update({"success_percentage": get_success_percentage(project_info)})

    project_info.pop('pipelines', None)
    return project_info


def print_report_project(info):
    print('''
    ======================== Gitlab Project Metrics =========================

    Project name  --------------------------------------  {0}
    Project id  ----------------------------------------  {1}

    report date  ---------------------------------------  {2}
    Pipeline moy duration  -----------------------------  {3}
    Pipeline success rate  -----------------------------  {4} %

    =========================================================================

    '''.format(info['name'],
               info['id'],
               datetime.date.today(),
               info['duration_in_minutes'],
               info['success_percentage']))
