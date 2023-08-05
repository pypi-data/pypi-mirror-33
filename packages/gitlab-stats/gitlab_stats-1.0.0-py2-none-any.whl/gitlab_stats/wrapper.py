from gitlab_stats.utils import *
import requests


class API(object):
    PROJECT_URL = "/api/v4/projects"
    PROJECTS_URL = PROJECT_URL + "?simple=true&"
    PER_PAGE = "per_page=100&page={0}"
    A_PIPELINE_URL = PROJECT_URL + "/{0}/pipelines/{1}"
    PIPELINES_URL = PROJECT_URL + "/{0}/pipelines?"

    def __init__(self, base_url="https://gitlab.com", token=None, proxies=""):
        requests.packages.urllib3.disable_warnings()

        token = check_token(token)
        self._proxies = proxies
        self._header = {'Content-Type': 'application/json', 'PRIVATE-TOKEN': '{0}'.format(token)}
        self.base_url = base_url

    def get(self, url):
        lookup_url = self.base_url + url
        with requests.Session() as s:
            response = s.get(lookup_url, proxies=self._proxies, headers=self._header, verify=False)

            if response.status_code != 200:
                raise ConnectionError("ConnexionError - Can't get to the gitlab api, check your token or the url")

            return response

    def get_through_page(self, url, action, pages=1):
        results = []
        lookup_url = url + API.PER_PAGE

        for page in range(1, pages + 1):
            r = self.get(lookup_url.format(page))
            results.extend(action(r.json()))

        return results

    def get_all_projects(self, pages=3):
        projects = self.get_through_page(
            API.PROJECTS_URL,
            get_name_and_id,
            pages
        )
        return projects

    def get_project_name(self, project_id):
        raw = self.get(API.PROJECT_URL + "/{}".format(project_id)).json()
        return raw['name']

    def get_all_pipelines_id_of(self, project_id, pages=1):
        pipelines = self.get_through_page(
            API.PIPELINES_URL.format(project_id),
            get_pipelines_id,
            pages
        )
        return pipelines

    def get_all_pipelines_info_of(self, project_id, pages=1):
        pipelines_info = []
        pipeline_list = self.get_all_pipelines_id_of(project_id, pages)

        for pipeline in pipeline_list:
            lookup_url = API.A_PIPELINE_URL.format(project_id, pipeline)
            pipelines_info.append(get_pipeline_info(self.get(lookup_url).json()))

        return pipelines_info

    def get_basic_project_info(self, project_id):
        projects = {'id': project_id,
                    'name': self.get_project_name(project_id),
                    'pipelines': self.get_all_pipelines_info_of(project_id)
                    }
        return projects

    def get_enhanced_project_info(self, project_id):
        projects = {'id': project_id,
                    'name': self.get_project_name(project_id),
                    'pipelines': self.get_all_pipelines_info_of(project_id)
                    }

        return enhance_project_info(projects)


if __name__ == "__main__":
    gaw = API()
    # gaw.get_all_projects()

    import tests
    # print(GitlabAPIWrapper.enhance_project_info(test.Test_PROJECT_INFO_DICT))

    info = enhance_project_info(tests.PROJECT_INFO)
    print(info)
    print_cli_report(info)
