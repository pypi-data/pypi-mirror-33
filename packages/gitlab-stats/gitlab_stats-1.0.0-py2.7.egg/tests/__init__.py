import os
from datetime import datetime

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
ENV_VAR_PATH = DATA_PATH = os.path.join(ROOT_PATH, "gitlab.env")

PROXIES = {'http': os.environ["PROXY"], 'https': os.environ["PROXY"]}
TEST_PROJECT_ID = 4895805
TEST_PROJECT_NAME = "integration-tests"

TEST_PROJECT_DICT = [
    {"id": 915, "description": "", "name": "project", "name_with_namespace": "Project / project name",
     "path": "path to project", "path_with_namespace": "I am getting bored of this",
     "created_at": "2018-06-08T18:18:39.029Z", "default_branch": "master",
     "forks_count": 0, "last_activity_at": "2018-06-15T14:42:54.278Z"}
]

TEST_PIPELINE_DICT = [
    {'id': 34692, "sha": "111edcb12207aec17aca660e957269fcc1a06356", "ref": "master", "status": "canceled"},
    {"id": 34501, "sha": "1cb7a4d8b1469a303dqqwe56877068610b9fdcb0", "ref": "master", "status": "success"},
    {"id": 34155, "sha": "b15e77c55bba9783fbwwqa24f17a304d86dde54c", "ref": "master", "status": "failed"},
    {"id": 32026, "sha": "6f52ae30eb543adecb81c74ca60253e62bcc586d", "ref": "master", "status": "skipped"},
]

TEST_PIPELINE_INFO_DICT = {
    "id": 33409, "sha": "d724e231065505afgwr2e6909e3baf4f90278", "ref": "master", "status": "success",
    "before_sha": "9396e122692cd0aa7a9c2dsfsb8f8efe97cc56", "tag": False, "yaml_errors": None,
    "user": {"id": 40, "name": "name", "username": "username", "state": "active"},
    "created_at": "2018-06-11T21:45:47.805Z",
    "updated_at": "2018-06-11T21:46:49.364Z", "started_at": "2018-06-11T21:45:49.574Z",
    "finished_at": "2018-06-11T21:46:49.359Z", "committed_at": None, "duration": 59, "coverage": None
}

# Duration moy - 58.9
TEST_PROJECT_INFO_DICT = {
    'id': TEST_PROJECT_ID, 'name': 'hlr-subscriber-api',
    'pipelines': [{'id': 34501, 'status': 'success', 'duration': 59, 'date': '2018-06-14'},
                  {'id': 34155, 'status': 'success', 'duration': 58, 'date': '2018-06-13'},
                  {'id': 33844, 'status': 'success', 'duration': 60, 'date': '2018-06-12'},
                  {'id': 33808, 'status': 'success', 'duration': 56, 'date': '2018-06-12'},
                  {'id': 33185, 'status': 'success', 'duration': 57, 'date': '2018-06-11'},
                  {'id': 33183, 'status': 'success', 'duration': 57, 'date': '2018-06-11'},
                  {'id': 33124, 'status': 'success', 'duration': 27, 'date': '2018-05-11'},
                  {'id': 31866, 'status': 'skipped', 'duration': 97, 'date': '2018-05-08'},
                  {'id': 31862, 'status': 'canceled', 'duration': 57, 'date': '2018-05-08'},
                  {'id': 31844, 'status': 'failed', 'duration': 61, 'date': '2018-05-08'}]
}

TEST_PROJECT_INFO_TIME_DICT = {
    'id': TEST_PROJECT_ID,
    'name': TEST_PROJECT_NAME,
    'pipelines': [{'id': 34501, 'status': 'success', 'duration': 59, 'date': datetime.now().strftime("%Y-%m-%d")},
                  {'id': 34155, 'status': 'success', 'duration': 58, 'date': datetime.now().strftime("%Y-%m-%d")},
                  {'id': 33844, 'status': 'success', 'duration': 60, 'date': datetime.now().strftime("%Y-%m-%d")},
                  {'id': 33808, 'status': 'success', 'duration': 56, 'date': datetime.now().strftime("%Y-%m-%d")},
                  {'id': 33185, 'status': 'success', 'duration': 57, 'date': datetime.now().strftime("%Y-%m-%d")},
                  {'id': 33183, 'status': 'success', 'duration': 57, 'date': datetime.now().strftime("%Y-%m-%d")},
                  {'id': 33124, 'status': 'success', 'duration': 27, 'date': '2018-05-11'},
                  {'id': 31866, 'status': 'skipped', 'duration': 97, 'date': '2018-05-08'},
                  {'id': 31862, 'status': 'canceled', 'duration': 57, 'date': '2018-05-08'},
                  {'id': 31844, 'status': 'failed', 'duration': 61, 'date': '2018-05-08'}]
}

TEST_PROJECT_INFO_ENHANCED = {'id': TEST_PROJECT_ID,
                              'name': TEST_PROJECT_NAME,
                              'pipelines': [{'id': 34501, 'status': 'success', 'duration': 59, 'date': '2018-06-14'},
                                            {'id': 34155, 'status': 'success', 'duration': 58, 'date': '2018-06-13'},
                                            {'id': 33844, 'status': 'success', 'duration': 60, 'date': '2018-06-12'},
                                            {'id': 33808, 'status': 'success', 'duration': 56, 'date': '2018-06-12'},
                                            {'id': 33185, 'status': 'success', 'duration': 57, 'date': '2018-06-11'},
                                            {'id': 33183, 'status': 'success', 'duration': 57, 'date': '2018-06-11'},
                                            {'id': 33124, 'status': 'success', 'duration': 27, 'date': '2018-05-11'},
                                            {'id': 31866, 'status': 'skipped', 'duration': 97, 'date': '2018-05-08'},
                                            {'id': 31862, 'status': 'canceled', 'duration': 57, 'date': '2018-05-08'},
                                            {'id': 31844, 'status': 'failed', 'duration': 61, 'date': '2018-05-08'}],
                              'duration_moy': 1.00,
                              'duration_in_minutes': '0 min 59s',
                              'success_percentage': 70
}
