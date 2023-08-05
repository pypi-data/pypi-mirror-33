import requests
import json
import threading
import os


class SpotlessError(Exception):
    """ A generic class for reporting errors from the spotless API """

    def __init__(self, reason):
        Exception.__init__(self, 'Spotless failed: reason %s' % reason)
        self.reason = reason


class SpotlessClient():
    """ The spotless client class for managing interaction with the Spotless API"""
    
    token = None                        # token is mandatory on instantiation
    url = None                          # standard spotless URL
    timeout = 60 * 10                   # default to 10 minutes timeout
    wait_time = 10                      # try every 10 seconds

    def __init__(self, **settings):
        """

        Creates a client for processing jobs in Spotless

        :type token: string
        :param token: The API token from your account on spotlessdata.com

        """
        for name, value in settings.items():
            if hasattr(self, name):
                setattr(self, name, value)

        if self.token is None:
            if 'SPOTLESS_API_TOKEN' in os.environ:
                self.token = os.environ['SPOTLESS_API_TOKEN']
            else:
                raise SpotlessError(reason='No Spotless API token passed and SPOTLESS_API_TOKEN environment variable not set')

        if self.url is None:
            if 'SPOTLESS_API_URL' in os.environ:
                self.url = os.environ['SPOTLESS_API_URL']
            else:
                self.url = "https://spotlessdata.com"

    def _get_id(self, url):
        if len(url.split('/')) > 1:
            return url.split('/')[-2]
        else:
            return url

    def _decode_response(self, response):
        if response.content != b'':
            return json.loads(response.content.decode('UTF-8'))
        else:
            return None

    def _unpack_json(self, list):
        s = ""
        for a in list:
            s = s + "\n%s : %s" % (a, list[a])
        return s

    def _decode_object_response(self, response, action, object_name):
        obj = self._decode_response(response)

        if response.status_code < 200 or response.status_code > 299:
            raise SpotlessError(reason='Error %s %s, response %s:%s' % (action,
                                                                        object_name,
                                                                        response.status_code,
                                                                        self._unpack_json(obj)))

        if obj is None:
            raise SpotlessError(reason='Empty content returned %s %s' % (action, object_name))
        return obj

    def _wait_for_completion(self, job, callback, remaining_attempts, *args):
        """ recursive function to call a timer until """

        if remaining_attempts == 0:
            raise SpotlessError(reason='Timeout reached')

        # call the callback once we have the completed job
        job = self.get_job(job["url"])
        self._validate_job(job)
        if job["processing_complete"]:
            callback(job, self, *args)
        else:
            threading.Timer(self.wait_time,
                            self._wait_for_completion,
                            [job, callback, remaining_attempts - 1] + list(args))

    def _validate_job(self, job):
        if job['exception_details'] != '':
            raise SpotlessError(job['exception_details'])
        return job

    def run_job(self, plan_url, file, *args):
        """

        Submit a job to spotless for processing

        :type plan_url: string
        :param plan_url: the URL of the plan on spotlessdata.com that you want to process the file against
        :type file: string
        :param file: The path to the file to be processed
        :type callback: function
        :param callback: The optional function you wish to have called once the job has been processed.
            The callback will receive a single parameter, the job which is contains the following fields:
            - url - the URL of the job
            - plan - the plan that was used to process the job
            - processing_complete - set to True if the processing is complete
            - processed_file - a link to download the processed file
            - history - details of the records that have been cleansed and links to quarantined records

        """
        with open(file, 'rb') as f:
            response = requests.post(
                "%s/api/jobs/" % self.url,
                headers={"Authorization": "Token " + self.token},
                data={"plan": self._get_id(plan_url)},
                files={"original_file": f}
            )

        job = self._decode_object_response(response, "creating", "job")

        if len(args) > 0:
            callback = args[0]
            new_args = [a for a in args if a != callback]
            self._wait_for_completion(job,
                                      callback,
                                      self.timeout / self.wait_time,
                                      *new_args)

        return self._validate_job(job)

    def _get_object(self, job_url, object_name):
        response = requests.get(
            job_url,
            headers={"Authorization": "Token " + self.token}
        )
        job = self._decode_object_response(response, "getting", object_name)

        return job

    def get_job(self, job_url):
        """
        Returns a job from a speciic URL. The job contains the following fields:
            - url - the URL of the job
            - plan - the plan that was used to process the job
            - processing_complete - set to True if the processing is complete
            - processed_file - a link to download the processed file
            - history - details of the records that have been cleansed and links to quarantined records
        """
        return self._validate_job(self._get_object(job_url, "job"))

    def delete_job(self, job):
        """
        Tells spotless that the job can be deleted, typically called once the cleansed data has been downloaded.
        """
        response = requests.patch(
            job["url"],
            headers={"Authorization": "Token " + self.token},
            data={"can_delete": True}
        )
        job = self._decode_object_response(response, "deleting", "job")

        return job

    def get_processed_file(self, job):
        """
        Downloads a file from a specified URL and provides it as a string
        """
        file = job["processed_file"]
        if file[0:4] == 'http':
            response = requests.get(job["processed_file"])
            if "=" in response.headers['Content-Type']:
                encoding=response.headers['Content-Type'].split("=")[-1] # noqa
                return response.content.decode(encoding)
            else:
                return response.content.decode('UTF-8')
        else:
            with open(file) as f:
                return file.read(f)

    def save_processed_file(self, job):
        """
        Downloads a file from a specified URL and provides it as a string
        """
        response = requests.get(job["processed_file"])
        encoding=response.headers['Content-Type'].split("=")[-1] # noqa
        return response.content.decode(encoding)

    def update_reference_rule_file(self, rule_url, file):
        
        with open(file, 'rb') as f:
            response = requests.patch(
                "%s/api/rule_reference/%s" % (self.url, rule_url),
                headers={"Authorization": "Token " + self.token},
                files={"reference_file": f}
            )
            rule = self._get_object(rule_url, "rule")

        return rule

