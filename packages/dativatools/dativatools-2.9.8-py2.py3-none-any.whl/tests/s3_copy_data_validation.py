import sys
import unittest
from dativatools.s3_lib import S3Lib
from dativatools.log import Logger
from boto.s3.connection import S3Connection

class test_s3_validation(unittest.TestCase):
    section = ''
    '''
    Class to perform testing of files upload/download from s3 bucket.
    '''
    config_dict = {'credentials': {'aws_access_key_id_optional': 'AKIAJCRXCZH3YAXIQ3UQ',
                                   'aws_secret_access_key_optional': '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',
                                   'environment_variables' : 'no',
                                   'bucket_name': 'gd-insight-reduced',
                                   'log_file_path': 'log/',
                                   'log_file_name':'s3_copy_data_valadation.txt'},
                   'insight_reduced': {'database': 'ci_demo_workflow_osn',
                                       'host': 'prod-demo-osn.cmiu8ugh2yx2.us-east-1.redshift.amazonaws.com',
                                       'port': 5439,
                                       'user': 'ardent',
                                       'password': 'Irdgd114',
                                       'client': 'pysopg2'},
                   's3bucketURL': 's3://gd-insight-reduced/',
				   'sub_dir': 'export_osn_3',
                   'backup_on_s3': 'back_up_csv_files/',
                   'suffix_schema':'etl',
                   'suffix_bkp':'_bkp',
                   'suffix_ren':'_ren',
                   'csv_path' :'/mnt/workflow/source_data_renuka',
                   'scriptfile': '/home/renuka/database_scripts/',
                   'ams': ['save_local_content_channel_info',
                        'save_local_content_programme_info',
                        'playback_local_info',
                        'playback_channel_info',
                        'playback_programme_info'],
                'non_ams': ['channel_info',
                            'schedule_info',
                            'ad_schedule_ad_info',
                            'ad_schedule_promo_info',
                            'application_info',
                            'asn_info',
                            'browser_info',
                            'cdn_info',
                            'demographic_info',
                            'device_info', 
                            'device_connection_type_info',
                            'geography_info',
                            'isp_info',
                            'package_info',
                            'purchasable_info',
                            'purchase_info',
                            'sso_info',
                            'subscriber_info',
                            'vod_info'],
                'loading_limit_dict': {'channel_info': 1, 'schedule_info': 1, 'ad_schedule_ad_info': 1,
                                       'ad_schedule_promo_info': 1, 'application_info': 1,
                                       'asn_info': 1, 'browser_info': 1, 'cdn_info': 1,
                                       'demographic_info': 1, 'device_info': 1,
                                       'device_connection_type_info': 1, 'geography_info': 1,
                                       'isp_info': 1, 'package_info': 1, 'purchasable_info': 1,
                                       'purchase_info': 1, 'sso_info': 1, 'subscriber_info': 1,
                                       'vod_info': 1},
               'fact_tables': ['gd_ci_ad_promo', 'gd_ci_consumption', 'gd_ci_ppv,gd_events', 'gd_ci_saved_content'],
               'final_tables': {'ad_schedule_ad_info': ['gdd_ad_promo_ad_schedule_ad_info',
                                                        'gdd_commercial_break_ad_schedule_ad_info',
                                                        'gdd_ad_schedule_ad_schedule_ad_info'],
                                'ad_schedule_promo_info': ['gdd_ad_promo_ad_schedule_promo_info',
                                                           'gdd_commercial_break_ad_schedule_promo_info',
                                                           'gdd_ad_schedule_ad_schedule_promo_info'],
                                'application_info': ['gdd_application_application_info'],
                                'asn_info': ['gdd_autonomous_system_number'],
                                'browser_info': ['gdd_browser'],
                                'cdn_info': ['gdd_cdn'],
                                'channel_info': ['gdd_channel',
                                                 'gdd_channel_attributes',
                                                 'gdd_channel_audio_language_channel_info'],
                                'consumption_method_info': ['gdd_consumption_method'],
                                'demographic_info': ['gdd_demographic'],
                                'device_connection_type_info': ['gdd_device_connection_type'],
                                'device_info': ['gdd_device', 'gdd_device_attributes'],
                                'geography_info': ['gdd_geography'],
                                'isp_info': ['gdd_isp'],
                                'package_info': ['gdd_package', 'gdd_channel_package'],
                                'playback_channel_info': ['gdd_session_playback_channel_info'],
                                'playback_local_info': ['gdd_session_playback_local_info'],
                                'playback_programme_info': ['gdd_session_playback_programme_info',
                                                            'gd_ci_consumption',
                                                            'gd_ci_ad_promo'],
                                'purchasable_info': ['gdd_purchasable'],
                                'purchase_info': ['gd_ci_ppv'],
                                'save_local_content_channel_info': ['gdd_save_result_save_local_content_channel_info',
                                                                    'gd_ci_saved_content_save_local_content_channel_info'],
                                'save_local_content_programme_info': ['gdd_save_result_save_local_content_programme_info',
                                                                      'gd_ci_saved_content_save_local_content_programme_info'],
                                'schedule_info': ['gdd_programme_schedule_info', 'gdd_epg'],
                                'sso_info': ['gdd_user_sso_info',
                                             'gdd_application_sso_info',
                                             'gd_events'],
                                'subscriber_info': ['gdd_subscriber',
                                                    'gdd_subscriber_attributes',
                                                    'gdd_subscriber_device',
                                                    'gdd_user_subscriber_info',
                                                    'gdd_subscriber_user',
                                                    'gdd_subscriber_package'],
                                'vod_info': ['gdd_programme_vod_info',
                                             'gdd_channel_audio_language_vod_info']
                                },
                'email_config':{
                    'send_from': 'integration.gd@ardentisys.com',
                    'send_to': 'renuka.lodaya@ardentisys.com',
                    'cc': 'renuka.lodaya@ardentisys.com',
                    'subject': 'GD Reduce Job Failure',
                    'smtplogin': 'integration.gd@ardentisys.com',
                    'smtppassword': '',
                    'smtpserver': 'mail.ardentisys.com:25'
                }
        }
				   
    logger = Logger()
    logger_obj = logger.__get_logger__(config_dict['credentials']['log_file_path'], config_dict['credentials']['log_file_name'])
    # -------------------------------------------------------------------------
    #    Name: test_copy_data()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is test that dat is copied from s3 to database.
    #          Provide ams or non-ams in config dict.           
    # -------------------------------------------------------------------------
    def test_copy_data(self):
        tableList = self.config_dict['non_ams']
        for tablename in tableList:
            obj,con = self.get_s3_val_obj()
            result = obj.copy_data(tablename,self.config_dict['sub_dir'])
            self.assertTrue(result[0], True)        

    # -------------------------------------------------------------------------
    #    Name: get_s3_val_obj()
    #    Returns: Settings
    #    Raises: None
    #    Desc: This function is used to pass the config details.
    # -------------------------------------------------------------------------
    def get_s3_val_obj(self):
        obj = S3Lib(self.config_dict, logger_obj=self.logger_obj )
        con = obj.get_connection(self.config_dict)[2] 
        return obj, con


'''
This function is used to initialize the test run
'''


if __name__ == '__main__':
    unittest.main()
