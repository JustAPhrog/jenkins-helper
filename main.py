from pathlib import Path, WindowsPath
from dotenv import load_dotenv
import os
import argparse
from time import sleep
from helper import Helper
import logging
import notifications
from progress.spinner import PieSpinner
from utils import convert_milliseconds_to_duration, json_to_obj


logger = logging.getLogger()

def setup_parser():
    parser = argparse.ArgumentParser(prog='Jenkins Helper')
    parser.add_argument('what_to_do', choices=['build_done', 'find_test', 'save_console_output', 'get_host', 'build_job'])
    parser.add_argument('-b', '--branch')
    parser.add_argument('--build', help='Define which build do you need. Default latest', default=None)
    parser.add_argument('--sleep', default=60, type=int)
    parser.add_argument('-t', '--test-case')
    parser.add_argument('-f', '--path-to-file')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('-p', '--parameters-path', help='Path to json with parameters')
    return parser

def build_done(helper: Helper):
    try:
        job_build = helper.get_build_info()
        logger.info('Causes: %s', helper.get_build_cause())
    except Exception as e:
        logger.error(e.with_traceback())
        return
    if job_build and job_build['inProgress']:
        try:
            counter = PieSpinner()
            job_stage = helper.get_current_stage()
            while job_build['inProgress']:
                if job_stage:
                    fullDuration = convert_milliseconds_to_duration(job_stage['fullDurationMillis'])
                    counter.message = '%s Job duration: %s step duration: %s ' % (job_stage['name'],
                                                                                fullDuration,
                                                                            convert_milliseconds_to_duration(job_stage['durationMillis']))
                else:
                    counter.message = 'Not started '
                counter.next()
                sleep(args.sleep)
                job_build = helper.get_build_info()
                job_stage = helper.get_current_stage()
        except KeyboardInterrupt:
            counter.finish()
            return
        counter.finish()
    build_info = helper.get_build_info()
    notification_str = 'Result: %s. %s' % (build_info['result'], build_info['url'])
    logger.info(notification_str)
    notifications.notify_win(title='Job done!', msg=notification_str, url=build_info['url'])
    for action in build_info['actions']:
        if '_class' in action.keys() and action['_class'] == 'hudson.tasks.junit.TestResultAction':
            failed = action['failCount']
            skipped = action['skipCount']
            total = action['totalCount']
            logger.info('Tests: failed: %s/%s, skipped: %s', failed, total, skipped)
            break


def find_test(helper: Helper):
    helper.get_test(args.test_case)

def get_host(helper: Helper):
    for host in helper.get_hosts():
        logger.info(host)

def save_console_output(helper: Helper, path_to_file):
    cons_log:str = helper.get_console_log()
    if not path_to_file.exists():
        path_to_file.touch()
    with path_to_file.open(mode='w', encoding='utf-8', newline='\n') as f:
        f.write(cons_log)

def build_job(helper: Helper):
    parameters_path = args.parameters_path
    params = json_to_obj(parameters_path)
    last_build_number = helper.get_latest_job_number()
    helper.build_job(params)
    current_build = helper.get_latest_build()
    logger.debug('Current build %s and latest %s', current_build['number'], last_build_number)
    i = 0
    while last_build_number == current_build['number']:
        if i == args.sleep:
            break
        i += 1
        sleep(1)
        current_build = helper.get_latest_build()
        logger.debug('(%i) Current: %s', i, current_build['number'])
    if i == args.sleep:
        logger.error('Build not start within %s second', i)
    else:
        logger.info('New build started #%s %s', current_build['number'], current_build['url'])

def work():
    JENKINS_URL = os.getenv('JENKINS_URL')
    helper = Helper(JENKINS_URL, os.getenv('JENKINS_USER'), os.getenv('JENKINS_TOKEN'))
    if not helper.if_logged():
        return
    helper.job_name = args.branch
    helper.build = args.build
    if args.what_to_do in ('build_done', 'get_host', 'find_test', 'save_console_output'):
        try:
            helper.search_for_job()
        except:
            logger.error('Not found %s:%s', helper.job_name, str(helper.build) if helper.build else 'latest')
            return
        
    if args.what_to_do == 'build_done':
        build_done(helper)
    elif args.what_to_do == 'find_test':
        find_test(helper)
    elif args.what_to_do == 'get_host':
        get_host(helper)
    elif args.what_to_do == 'save_console_output':
        results = Path('results')
        if not results.is_dir():
            results.mkdir()
        save_console_output(helper, Path(results, args.path_to_file))
    elif args.what_to_do == 'build_job':
        build_job(helper)
    else:
        logger.error('Not implemented: %s', args.what_t_do)


if __name__ == '__main__':
    parser = setup_parser()
    args = parser.parse_args()
    log_level = logging.INFO
    log_format = '%(levelname)s|%(module)s:%(lineno)d - %(message)s'
    if args.debug:
        log_format = '%(name)s:%(lineno)d - %(levelname)s - %(message)s'
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format=log_format)
    logger_urlib = logging.getLogger('urllib3')
    if logger_urlib.name == 'urllib3':
        logger_urlib.setLevel(logging.WARNING)

    load_dotenv()
    work()
        