from threading import Thread
from time import sleep
import requests

from configuration import APP_CONFIG

base_url = f'http://localhost:{APP_CONFIG.GLOBAL["listen_port"]}{APP_CONFIG.GLOBAL["API_root"]}'


def view_request(table, topic=None):
    if topic is not None:
        requests.get(f'{base_url}viewer?token={APP_CONFIG.TOKEN}&table={table}&topic={topic}')
    else:
        requests.get(f'{base_url}viewer?token={APP_CONFIG.TOKEN}&table={table}')


def write_request(topic, state):
    requests.get(f'{base_url}write?token={APP_CONFIG.TOKEN}&topic={topic}&state={state}')


def read_request(topic):
    requests.get(f'{base_url}read?token={APP_CONFIG.TOKEN}&topic={topic}')


if __name__ == "__main__":
    for salvo in range(1000):
        for task in range(10):
            Thread(target=write_request, args=("simulator", salvo)).start()
            Thread(target=write_request, args=("simulator", task)).start()
            # Thread(target=view_request, args=("topics")).start()
            # Thread(target=view_request, args=("history", salvo)).start()
            # Thread(target=view_request, args=("topics", "simulator")).start()

            print(f'salvo: {salvo} / task: {task}')

        sleep(0)
