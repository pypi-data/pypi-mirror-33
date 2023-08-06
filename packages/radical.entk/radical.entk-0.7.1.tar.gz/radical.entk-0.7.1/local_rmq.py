from radical.entk import Pipeline, Stage, Task, AppManager
import pytest
from radical.entk.exceptions import *
import os

hostname = os.environ.get('RMQ_HOSTNAME','localhost')
port = int(os.environ.get('RMQ_PORT',5672))

def create_single_task():

    t1 = Task()
    t1.name = 'simulation'
    t1.executable = ['/bin/sleep']
    t1.arguments = ['10']
    t1.copy_input_data = []
    t1.copy_output_data = []

    return t1

NUM_TASKS = 8192

if __name__ == '__main__':

    p1 = Pipeline()
    p1.name = 'p1'

    s = Stage()
    s.name = 's1'

    for t in range(NUM_TASKS):
        s.add_tasks(create_single_task())

    p1.add_stages(s)

    res_dict = {

            'resource': 'xsede.supermic',
            'walltime': 30,
            'cores': 1000,
            'project': 'TG-MCB090174'

    }

    appman = AppManager(rts='radical.pilot')
    appman.resource_desc = res_dict
    appman.assign_workflow(set([p1]))
    appman.run()
