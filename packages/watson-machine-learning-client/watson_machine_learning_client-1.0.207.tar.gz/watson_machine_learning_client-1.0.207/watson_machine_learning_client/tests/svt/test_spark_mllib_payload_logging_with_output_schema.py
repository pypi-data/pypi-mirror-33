import unittest
from watson_machine_learning_client.log_util import get_logger
from preparation_and_cleaning import *
from models_preparation import *
import psycopg2

postgres_connection = {
    "type": "postgresql",
    "database": "compose",
    "user": "admin",
    "password": "JIILAWZGGFYLJZOH",
    "host": "sl-us-south-1-portal.21.dblayer.com",
    "port": "42618",
    "tablename": "spark_mllib_payload_logging_test_table"
}



class TestWMLClientWithSpark(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    scoring_url = None
    labels = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestWMLClientWithSpark.logger.info("Service Instance: setting up credentials")

        self.wml_credentials = get_wml_credentials()
        self.client = get_client()

    def test_00_check_client_version(self):
        TestWMLClientWithSpark.logger.info("Check client version...")

        self.logger.info("Getting version ...")
        version = self.client.version
        TestWMLClientWithSpark.logger.debug(version)
        self.assertTrue(len(version) > 0)

    def test_01_service_instance_details(self):
        TestWMLClientWithSpark.logger.info("Check client ...")
        self.assertTrue(self.client.__class__.__name__ == 'WatsonMachineLearningAPIClient')

        self.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()
        TestWMLClientWithSpark.logger.debug(details)

        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_02_publish_model(self):
        TestWMLClientWithSpark.logger.info("Creating spark model ...")

        model_data = create_spark_mllib_model_data()
        TestWMLClientWithSpark.labels = model_data['labels']
        print(dir(model_data['model']))

        TestWMLClientWithSpark.logger.info("Publishing spark model ...")

        self.client.repository.ModelMetaNames.show()

        model_props = {self.client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
                       self.client.repository.ModelMetaNames.NAME: "spark payload logging model"
                       }

        TestWMLClientWithSpark.logger.info(model_data['pipeline'])
        TestWMLClientWithSpark.logger.info(type(model_data['pipeline']))

        published_model = self.client.repository.store_model(model=model_data['model'], meta_props=model_props, training_data=model_data['training_data'], pipeline=model_data['pipeline'])
        TestWMLClientWithSpark.model_uid = self.client.repository.get_model_uid(published_model)
        TestWMLClientWithSpark.logger.info("Published model ID:" + str(TestWMLClientWithSpark.model_uid))
        self.assertIsNotNone(TestWMLClientWithSpark.model_uid)

    def test_03_get_details(self):
        TestWMLClientWithSpark.logger.info("Get model details")
        details = self.client.repository.get_details(self.model_uid)
        TestWMLClientWithSpark.logger.debug("Model details: " + str(details))
        self.assertTrue("spark payload logging model" in str(details))

        details_all = self.client.repository.get_details()
        TestWMLClientWithSpark.logger.debug("All artifacts details: " + str(details_all))
        self.assertTrue("spark payload logging model" in str(details_all))

        details_models = self.client.repository.get_model_details()
        TestWMLClientWithSpark.logger.debug("All models details: " + str(details_models))
        self.assertTrue("spark payload logging model" in str(details_models))

    def test_04_create_deployment(self):
        TestWMLClientWithSpark.logger.info("Create deployments")
        deployment = self.client.deployments.create(model_uid=self.model_uid, name="Test deployment", asynchronous=False)
        TestWMLClientWithSpark.logger.info("model_uid: " + self.model_uid)
        TestWMLClientWithSpark.logger.info("Online deployment: " + str(deployment))
        self.assertTrue(deployment is not None)
        TestWMLClientWithSpark.scoring_url = self.client.deployments.get_scoring_url(deployment)
        TestWMLClientWithSpark.deployment_uid = self.client.deployments.get_uid(deployment)
        self.assertTrue("online" in str(deployment))
        self.client.deployments.get_status(TestWMLClientWithSpark.deployment_uid)

    def test_05_enable_payload_logging(self):
        TestWMLClientWithSpark.logger.info("Setup payload logging")
        payload_logging_configuration = {
            self.client.deployments.PayloadLoggingMetaNames.PAYLOAD_DATA_REFERENCE: {
                "type": postgres_connection['type'],
                "location": {
                    "tablename": postgres_connection['tablename']
                },
                "connection": {
                    "uri": "postgres://{}:{}@{}:{}/{}".format(
                        postgres_connection['user'],
                        postgres_connection['password'],
                        postgres_connection['host'],
                        postgres_connection['port'],
                        postgres_connection['database']
                    )
                }
            },
            "labels": [
                'Camping Equipment',
                'Personal Accessories',
                'Mountaineering Equipment',
                'Golf Equipment',
                'Outdoor Protection'
            ],
            "output_data_schema": {
               'fields':[
                  {
                     'type':'string',
                     'nullable':True,
                     'name':'GENDER',
                     'metadata':{

                     }
                  },
                  {
                     'type':'integer',
                     'nullable':True,
                     'name':'AGE',
                     'metadata':{

                     }
                  },
                  {
                     'type':'string',
                     'nullable':True,
                     'name':'MARITAL_STATUS',
                     'metadata':{

                     }
                  },
                  {
                     'type':'string',
                     'nullable':True,
                     'name':'PROFESSION',
                     'metadata':{

                     }
                  },
                  {
                     'type':'double',
                     'nullable':True,
                     'name':'prediction',
                     'metadata':{
                        'modeling_role':'prediction'
                     }
                  },
                  {
                     'type':{
                        'type':'array',
                        'elementType':'double',
                        'containsNull':True
                     },
                     'nullable':True,
                     'name':'probability',
                     'metadata':{
                        'modeling_role':'probability'
                     }
                  }
               ],
               'type':'struct'
            }
        }
        print(TestWMLClientWithSpark.labels)

        self.client.deployments.setup_payload_logging(TestWMLClientWithSpark.deployment_uid, payload_logging_configuration)

    def test_06_get_payload_logging_details(self):
        payload_logging_details = self.client.deployments.get_payload_logging_details(TestWMLClientWithSpark.deployment_uid)
        self.assertTrue(payload_logging_details is not None)

    def test_07_get_deployment_details(self):
        TestWMLClientWithSpark.logger.info("Get deployment details")
        deployment_details = self.client.deployments.get_details()
        self.assertTrue("Test deployment" in str(deployment_details))

    def test_08_clean_db(self):
        conn = psycopg2.connect(
            database=postgres_connection['database'],
            user=postgres_connection['user'],
            password=postgres_connection['password'],
            host=postgres_connection['host'],
            port=postgres_connection['port']
        )
        cur = conn.cursor()
        cur.execute("DELETE from " + postgres_connection['tablename'] + ";")
        conn.commit()
        print("Total number of rows deleted :", cur.rowcount)
        cur.execute("SELECT * from " + postgres_connection['tablename'])
        rows = cur.fetchall()

        conn.close()

        self.assertTrue(len(rows) == 0)

    def test_09_score(self):
        TestWMLClientWithSpark.logger.info("Score the model")
        scoring_data = {"fields": ["GENDER", "AGE", "MARITAL_STATUS", "PROFESSION"], "values": [["M", 23, "Single", "Student"], ["M", 55, "Single", "Executive"]]}
        predictions = self.client.deployments.score(TestWMLClientWithSpark.scoring_url, scoring_data)
        TestWMLClientWithSpark.logger.debug("Predictions: {}".format(predictions))
        self.assertTrue("prediction" in str(predictions))

    def test_10_check_db_content(self):
        conn = psycopg2.connect(
            database=postgres_connection['database'],
            user=postgres_connection['user'],
            password=postgres_connection['password'],
            host=postgres_connection['host'],
            port=postgres_connection['port']
        )
        cur = conn.cursor()
        cur.execute("SELECT * from " + postgres_connection['tablename'])
        rows = cur.fetchall()
        for row in rows:
            print("ID = ", row, "\n")

        conn.close()

        self.assertTrue(len(rows) == 2)

    def test_11_delete_payload_logging(self):
        self.client.deployments.delete_payload_logging(TestWMLClientWithSpark.deployment_uid)

    def test_12_delete_deployment(self):
        TestWMLClientWithSpark.logger.info("Delete deployment")
        self.client.deployments.delete(TestWMLClientWithSpark.deployment_uid)

    def test_13_delete_model(self):
        TestWMLClientWithSpark.logger.info("Delete model")
        self.client.repository.delete(TestWMLClientWithSpark.model_uid)


if __name__ == '__main__':
    unittest.main()
