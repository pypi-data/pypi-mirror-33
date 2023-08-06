from json import dumps

from docker import from_env
from ws4py.client.threadedclient import WebSocketClient

from ..config import ROOT_DIR, WS_ADDRESS


def write_docker_log(pivot, verbosity, host=None, tls=True):
    client = from_env()
    container_lists = client.containers.list()
    if len(container_lists) > 0:
        ws = WebSocketClient(url=WS_ADDRESS)
        try:
            ws.connect()
            for container in container_lists:
                for line in container.logs(stream=True):
                    with open('%s/result/%s.log' % (ROOT_DIR, container.attrs['Id']), 'a') as f:
                        f.writelines(line)
                    ws.send(dumps({
                        'type': 'eubh',
                        'project_machine_id': pivot.get('id'),
                        'data': line
                    }))
        except:
            if verbosity:
                print("Tail container error")
            ws.close()
            write_docker_log(pivot, verbosity)
    else:
        if verbosity:
            print("No container found")


class ContainerLog:
    def __init__(self, pivot, verbosity, host=None, webscoket=WS_ADDRESS):
        write_docker_log(pivot, verbosity, host, webscoket)
