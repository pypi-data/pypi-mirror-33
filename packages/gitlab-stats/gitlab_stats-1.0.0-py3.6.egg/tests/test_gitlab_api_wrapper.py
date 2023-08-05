import tests
import time
import unittest
from gitlab_stats.utils import *
from gitlab_stats.wrapper import API


class APITest(unittest.TestCase):

    def setUp(self):
        self.gaw = API(proxies=tests.PROXIES)
        self._started_at = time.time()

    def tearDown(self):
        elapsed = time.time() - self._started_at
        print('({}s) - {}'.format(round(elapsed, 2), self.id()[56:]))

    # -- API connexion and information retrieve

    @unittest.skip
    def test_001_get_response(self):
        response = self.gaw.get(API.PROJECT_URL)
        self.assertEqual(response.status_code, 200,
                         "Can't reach this url, it can be your proxy or a wrong token, set them in a .env file")

    def test_002_no_token_raise_error(self):
        with self.assertRaises(KeyError):
            """ Can't really test this """
            import os
            print(os.environ["NOT_WHERE_TOKEN_IS_STORED"])  # This will raise a key error
            API()  # Should happen here too when no token in GITLAB_TOKEN

    def test_003_wrong_token_raise_error(self):
        with self.assertRaises(ConnectionError):
            self.gaw._header = {'Content-Type': 'application/json', 'PRIVATE-TOKEN': '{0}'.format("wrong token")}
            self.gaw.get_project_name(tests.TEST_PROJECT_ID)

    # -- Get project info

    @unittest.skip
    def test_010_get_project_name_from_id(self):
        response = self.gaw.get_project_name(tests.TEST_PROJECT_ID)
        self.assertEquals(response, tests.TEST_PROJECT_NAME)

    @unittest.skip
    def test_011_get_all_projects(self):
        response = self.gaw.get_all_projects(1)
        self.assertEqual(type(response), list)
        self.assertEqual(type(response[0]), dict, "Project id and name should be in a dict")

    @unittest.skip
    def test_012_get_all_projects_and_correct_fields(self):
        response = self.gaw.get_all_projects(1)
        self.assertTrue('id' in response[0])
        self.assertTrue('name' in response[0])

    @unittest.skip
    def test_013_get_project_information(self):
        response = self.gaw.get_basic_project_info(tests.TEST_PROJECT_ID)
        self.assertEqual(len(response), 3)
        self.assertTrue('id' in response)
        self.assertTrue('name' in response)
        self.assertTrue('pipelines' in response)

    @unittest.skip
    def test_014_get_enhanced_project_information(self):
        response = self.gaw.get_enhanced_project_info(tests.TEST_PROJECT_ID)
        self.assertEqual(len(response), 5)
        self.assertTrue('id' in response)
        self.assertTrue('name' in response)
        self.assertTrue('duration_moy' in response)
        self.assertTrue('duration_in_minutes' in response)
        self.assertTrue('success_percentage' in response)

    # -- Get pipeline info

    @unittest.skip
    def test_020_get_all_pipelines_of_a_project(self):
        response = self.gaw.get_all_pipelines_id_of(tests.TEST_PROJECT_ID)
        self.assertEqual(type(response), list)
        self.assertEqual(type(response[0]), int, "Pipeline id should be a int")

    @unittest.skip
    def test_021_get_all_pipelines_info_of_a_project(self):
        response = self.gaw.get_all_pipelines_info_of(tests.TEST_PROJECT_ID)
        self.assertEqual(type(response), list)
        self.assertEqual(type(response[0]), dict, "Pipeline info should be a dict")

    @unittest.skip
    def test_022_get_all_pipelines_info_and_correct_fields(self):
        response = self.gaw.get_all_pipelines_info_of(tests.TEST_PROJECT_ID)
        self.assertTrue('id' in response[0])
        self.assertTrue('status' in response[0])
        self.assertTrue('duration' in response[0])
        self.assertTrue('date' in response[0])

    # -- Project name and id

    def test_030_get_name_and_id_in_a_list_of_dict(self):
        response = get_name_and_id(tests.TEST_PROJECT_DICT)
        self.assertEqual(type(response), list)
        self.assertEqual(type(response[0]), dict)

    def test_031_get_name_and_id_has_correct_fields(self):
        response = get_name_and_id(tests.TEST_PROJECT_DICT)
        self.assertEqual(len(response[0]), 2)
        self.assertEqual(response[0]['id'], 915)
        self.assertEqual(response[0]['name'], 'project')

    # -- Pipeline

    def test_040_get_pipeline_id_in_a_list(self):
        response = get_pipelines_id(tests.TEST_PIPELINE_DICT)
        self.assertEqual(type(response), list)

    def test_041_get_pipeline_id_in_a_dict_has_correct_fields(self):
        response = get_pipelines_id(tests.TEST_PIPELINE_DICT)
        self.assertEqual(type(response), list)
        self.assertEqual(len(response), 4)
        self.assertEqual(response[0], 34692)

    def test_042_get_pipeline_info_in_a_dict(self):
        response = get_pipeline_info(tests.TEST_PIPELINE_INFO_DICT)
        self.assertEqual(type(response), dict)

    def test_043_get_pipeline_info_with_correct_fields(self):
        response = get_pipeline_info(tests.TEST_PIPELINE_INFO_DICT)
        self.assertEqual(len(response), 4)
        self.assertTrue('id' in response)
        self.assertTrue('status' in response)
        self.assertTrue('duration' in response)
        self.assertTrue('date' in response)

    # -- Value added

    def test_050_get_moy_duration(self):
        duration_moy = get_duration_moy(tests.TEST_PROJECT_INFO_DICT)
        print(duration_moy)
        self.assertEqual(duration_moy, 58.9)

    def test_051_get_success_percentage(self):
        success_percentage = get_success_percentage(tests.TEST_PROJECT_INFO_DICT)
        self.assertEqual(success_percentage, 70)

    def test_052_get_all_pipeline_info_from_2_weeks_ago(self):
        response = get_pipeline_info_from(tests.TEST_PROJECT_INFO_TIME_DICT, 15)
        self.assertEqual(len(response['pipelines']), 6)

    def test_053_enhance_project_info(self):
        response = enhance_project_info(tests.TEST_PROJECT_INFO_DICT)
        self.assertEqual(len(response), 5)
        self.assertTrue('id' in response)
        self.assertTrue('name' in response)
        self.assertTrue('duration_moy' in response)
        self.assertTrue('duration_in_minutes' in response)
        self.assertTrue('success_percentage' in response)

    def test_55_get_report(self):
        print_report_project(tests.TEST_PROJECT_INFO_ENHANCED)


if __name__ == "__main__":
    unittest.main()
