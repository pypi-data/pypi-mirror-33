import logging
import os
import time

try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError
import requests

log = logging.getLogger('allgo')
__version__ = '0.1.10'


def local_token():
    from os.path import expanduser
    home = expanduser("~")
    filetoken = os.path.join(home, '.allgo_token')
    if os.path.exists(filetoken):
        with open(filetoken) as f:
            return f.read()

class App:
    """
    AllGo app submission object
    """

    def __init__(self, name, token=None):
        """
        Constructor
        :param name: name of the application in lower case
        :param token: if not provided, we check ALLGO_TOKEN env variable and notebook parameters
        """
        self.name = name
        if token:
            self.token = token
        elif 'ALLGO_TOKEN' in os.environ.keys():
            self.token = os.environ.get('ALLGO_TOKEN')
        elif local_token():
            self.token = local_token()
        else:
            raise Exception("You must provide a token in parameter or define an environment variable 'ALLGO_TOKEN'")

    def run(self, files, outputdir='.', params=''):
        """
        Submit the job
        :param files: input files
        :param outputdir: by default current directory
        :param params: a string parameters see the application documentation
        :return:
        """
        headers = {'Authorization': 'Token token={}'.format(self.token)}
        data = {"job[webapp_name]": self.name,
                "job[webapp_id]": self.name,
                "job[param]": params}
        ALLGO_URL = os.environ.get('ALLGO_URL', "https://allgo.inria.fr")
        r = requests.post('%s/api/v1/jobs' % ALLGO_URL, headers=headers, files=files, data=data)
        r.raise_for_status()
        r = r.json()
        jobid = r['id']
        results = None
        while True:
            r = requests.get('{}/api/v1/jobs/{}'.format(ALLGO_URL, jobid), headers=headers)
            r.raise_for_status()
            results = r.json()
            status = results['status']
            if status in ['created', 'waiting', 'running', 'in progress']:
                log.info("wait for job %s in status", jobid, status)
                time.sleep(2)
            else:
                break

        if status != 'done':
            raise Exception('Job %s failed with status %s', (jobid, status))

        elif status == 'done' and results:
            for filename, url in results[str(jobid)].items():
                filepath = os.path.join(outputdir, filename)
                with open(filepath, 'wb') as fb:
                    fb.write(requests.get(url, stream=True).content)
