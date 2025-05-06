import functools
import json
import re
from jenkins import Jenkins
import logging

class Helper:

    def __init__(self, url, username=None, password=None):
        self.logger = logging.getLogger(__name__)
        self.j = Jenkins(url, username, password)
        self.job_name = str()
        self.build = str()
    
    
    def if_logged(self):
        try:
            me = self.j.get_whoami()
            self.logger.info('Hello %s', me['fullName'])
            return True
        except Exception as e:
            self.logger.error('Not logged or server not responding: %s', e)
            return False
    
    def search_for_job(self, if_regex_job=False):
        self.logger.debug('Selected job %s', self.job_name)
        if if_regex_job:
            found_jobs = self.j.get_job_info_regex(self.job_name, folder_depth=1)
            if len(found_jobs) == 0:
                return False
            self.job_name = found_jobs[0]['fullName']
            self.build = found_jobs[0]['lastBuild']['number'] if self.build is None else self.build
        else:
            found_jobs = self.j.get_job_info(self.job_name)
            self.job_name = found_jobs['fullName']
            self.build = found_jobs['lastBuild']['number'] if self.build is None else self.build
        self.logger.info('Found job %s:%s', self.job_name, self.build)
        return True

    def get_build_info(self) -> dict | None:
        self.logger.debug('Looking for build %s:%s', self.job_name, self.build)
        return self.j.get_build_info(self.job_name, self.build)
    
    def get_latest_job_number(self) -> str | None:
        return self.j.get_job_info(self.job_name)['lastBuild']['number']
    
    def get_latest_build(self) -> dict | None:
        return self.j.get_job_info(self.job_name)['lastBuild']
    
    def get_build_cause(self) -> list:
        results = []
        actions:list = self.get_build_info()['actions']
        for action in actions:
            if '_class' in action.keys() and action['_class'] == 'hudson.model.CauseAction':
                for cause in action['causes']:
                    if 'shortDescription' in cause.keys():
                        results.append(cause['shortDescription'])
        return results
    
    def get_current_stage(self) -> dict | None:
        stages = self.get_build_stages()
        for stage in stages['stages']:
            if stage['status'] == 'IN_PROGRESS':
                stage['fullDurationMillis'] = stages['durationMillis']
                return stage
        return None
    
    def get_build_stages(self) -> dict | None:
        return self.j.get_build_stages(self.job_name, self.build)

    def build_job(self, parameters):
        self.j.build_job(self.job_name, parameters)
    
    
    def get_test(self, test_name):
        test_info:dict = self.j.get_build_test_report(self.job_name, self.build)
        if not test_info or len(test_info['suites']) == 0:
            return None
        for test_suite in test_info['suites']:
            self.logger.info('Searching: %s', test_suite['enclosingBlockNames'][0])
            if len(test_suite) > 0:
                print(len(test_info['suites']))
                for test_case in test_suite['cases']:
                    if test_case['name'].find(test_name):
                        self.logger.info('Found %s', test_case['name'])
                        return test_case
        return None
    
    def get_console_log(self) -> str:
        return self.j.get_build_console_output(self.job_name, self.build)
    
    def get_progressive_console_log(self) -> str:
        return self.j.get_build_progressive_output(self.job_name, self.build)
    
    def get_hosts(self) -> list:
        build_info = self.get_build_info()
        if build_info and build_info['description']:
            return build_info['description'].split('\n\n')[2].split('\n')
        return None