import multiprocessing
import subprocess
import os
import signal
from uuid import getnode as get_mac

import docker
from apscheduler.schedulers.background import BlockingScheduler
from click import echo

import api
import get
import put
import status
import utils
from config import WS_ADDRESS, ROOT_DIR, DOCKER_WHITE_LIST, HTTP_ADDRESS
from logs.container_log import ContainerLog as WriteContainerLog
from wesockets.container_log import ContainerLog as PushContainerLog


def clean_file():
    echo('Remove %s/code and %s/result' % (ROOT_DIR, ROOT_DIR))
    os.popen('rm -rf %s/code %s/result' % (ROOT_DIR, ROOT_DIR))
    echo('Remove files successful.')


def create_directories():
    os.makedirs('%s/code' % ROOT_DIR)
    os.makedirs('%s/result' % ROOT_DIR)


def job_write_log(data, verbosity, host=HTTP_ADDRESS, webscoket=WS_ADDRESS):
    WriteContainerLog(pivot=data, verbosity=verbosity, host=host, webscoket=webscoket)


def job_real_time_push_log(data):
    push_container_log = PushContainerLog(WS_ADDRESS, data)

    try:
        push_container_log.connect()
    except KeyboardInterrupt:
        push_container_log.close()


def job_start_miner(cmd,fileout):
    if not utils.is_empty(cmd):
        try:
            p = subprocess.Popen(cmd, shell=True, stdout=fileout)
            return p.pid
        except:
            echo('Running minner fail.')
            return 0
    else:
        return 0


class Watch:
    def __init__(self, key, time, verbosity, host, webscoket, miner, outname):
        self.time = time
        self.key = key
        self.host = host
        self.webscoket = webscoket
        self.miner = miner
        self.outname=outname
        self.api = api.Api(base_url=host)
        print("Api server:%s ,Webscoket:%s" % (webscoket, host))
        self.docker_client = docker.from_env()
        self.can_init = True
        self.cache_log = []
        self.jobs = []
        self.is_verbose = True if verbosity else False
        self.pid = 0
        self.mtime = 0
        self.fileout = open(self.outname, 'w')

    # def close_all_jobs(self):
    #     for job in self.jobs:
    #

    def clean_docker(self):
        client = self.docker_client
        for container in client.containers.list():
            if container.attrs['Name'] not in DOCKER_WHITE_LIST:
                container.stop()

    def run_cmd_and_upload_result(self, pivot):
        cmd = pivot.get('cmd')
        if not utils.is_empty(cmd):
            cmd_result_out_put = os.popen(cmd)
            cmd_result_out_put_string = cmd_result_out_put.read()
            self.api.project_machine_update_cmd({"id": pivot.get('id'), "result": cmd_result_out_put_string})
            cmd_result_out_put.close()

    def upload_machine_information(self):
        client = self.docker_client
        current_status = status.Status.IDLE.value

        client_containers_count = len(client.containers.list())
        if client_containers_count == 0:
            if not utils.is_empty(self.key):
                current_status = status.Status.COMPLETE.value
        else:
            current_status = status.Status.IDLE.value

        if client_containers_count > 0:
            if utils.is_empty(self.key):
                self.clean_docker()
                current_status = status.Status.IDLE.value
            else:
                current_status = status.Status.RUNNING.value
        """

        client_containers_count = len(client.containers.list())
        if utils.is_empty(self.key):
            current_status = status.Status.IDLE.value
            if client_containers_count > 0:
                self.clean_docker()

        elif client_containers_count == 0:
            current_status = status.Status.COMPLETE.value
        elif client_containers_count > 0:
            current_status = status.Status.RUNNING.value

        """

        data = utils.get_device_info()
        data['status_info'] = {
            'key': self.key,
            'status': current_status
        }
        data['mac'] = "machine_%s" % get_mac()
        response = self.api.upload_machine_and_get_task(data)

        if self.is_verbose:
            print(data, response)

        if type(response) is not list:
            option = response.get('option')
            project = response.get('project')
            pivot = response.get('pivot')

            key = None
            if project is not None:
                key = project.get('key')

            if not utils.is_empty(key):

                if self.pid != 0:
                    os.kill(self.pid, signal.SIGKILL)
                    os.kill(self.pid + 1, signal.SIGKILL)
                    self.pid = 0
                    self.mtime = 0

                if option == 'init' and self.can_init:
                    self.can_init = False
                    if len(self.jobs) > 0:
                        for job in self.jobs:
                            job.terminate()
                    clean_file()
                    create_directories()
                    get.Get(key).get(ROOT_DIR, True, self.host)
                    self.key = key
                    self.run_cmd_and_upload_result(pivot)
                    # real_time_push_log = multiprocessing.Process(target=job_real_time_push_log, args=(pivot,))
                    # real_time_push_log.start()
                    #
                    # self.jobs.append(real_time_push_log)

                    write_log = multiprocessing.Process(target=job_write_log,
                                                        args=(pivot, self.is_verbose, self.host, self.webscoket))
                    write_log.start()

                    self.jobs.append(write_log)

                elif option == 'cmd':
                    self.run_cmd_and_upload_result(pivot)

            if option == 'clean':
                self.clean_docker()
                if not utils.is_empty(self.key):
                    put.Put(self.key, 'result').put('%s/result' % ROOT_DIR, True, self.host)
                    self.key = ''
                    self.can_init = True

        if self.pid == 0 :
            self.mtime = self.mtime + 1
            if self.mtime >= 30 and current_status == status.Status.IDLE.value and utils.is_empty(key):
                self.pid = job_start_miner(self.miner,self.fileout)
                self.mtime = 0
        elif self.pid != 0:
            self.mtime = self.mtime + 1
            if self.mtime > 90:
                os.kill(self.pid, signal.SIGKILL)
                os.kill(self.pid + 1, signal.SIGKILL)
                self.pid = 0
                self.mtime = 0

    def log_is_exist(self, container_id, log):
        cache_logs = self.cache_log
        is_exist_log = False
        for i in cache_logs:
            if cache_logs[i].container_id == container_id and cache_logs[i].log == log:
                is_exist_log = True
                break
        if not is_exist_log:
            self.cache_log.append({
                container_id: container_id,
                log: log
            })
        return is_exist_log

    def watch_upload_docker_log(self):
        client = self.docker_client

        for container in client.containers.list():
            log = container.logs()

            self.api.post_project_container_logs({
                'container_id': container.attrs['Id'],
                'log': log
            })

    def watch(self):
        scheduler = BlockingScheduler()
        scheduler.add_job(self.upload_machine_information, 'interval', seconds=self.time, max_instances=1)
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
