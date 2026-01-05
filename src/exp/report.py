from matplotlib import pyplot as plt
from uuid import uuid4
import json
import os
import time


def get_context_key(context):
    if context is None:
        return ''
    return '-'.join([f'{k}:{context[k]}' for k in sorted(context.keys())])

class Report:

    def __init__(self, name='', repo=None, run_id=None, tag='', flush_interval=5):
        if run_id is not None:
            self.run_id = run_id
        else:
            self.run_id = str(uuid4())

        self.start_time = time.time()
        self.last_update = time.time()
        self.flush_interval = flush_interval
        self.name = name
        self.tag = tag
        self.repo = repo if repo is not None else os.getcwd()
        self.params = {}
        self.logs = {}
        self.current_step = 0

    def log(self, data, context=None):
        self.last_update = time.time()
        for k, v in data.items():
            metric_key = f'{k}-{get_context_key(context)}'
            if metric_key not in self.logs:
                if type(v) is dict:
                    self.logs[metric_key] = {'name': k, 'context': context, **{sub_k: [] for sub_k in v.keys()}}
                else:
                    self.logs[metric_key] = {'name': k, 'context': context, 'y': []}

            if type(v) is dict:
                for sub_v in v.keys():
                    self.logs[metric_key][sub_v].append(v[sub_v])
            else:
                self.logs[metric_key]['y'].append(v)

        self.current_step += 1
        if self.current_step % self.flush_interval == 0:
            self.save()

    def plot(self, metrics):
        if list in [type(x) for x in metrics]:
            fig, ax = plt.subplots(1, len(metrics), figsize=(12, 4))

            for i, metric_group in enumerate(metrics):

                for metric in metric_group:
                    ax[i].plot(self.logs[metric], label=metric)

                ax[i].legend()

            fig.tight_layout()
            plt.show()
            return
        for metric in metrics:
            plt.plot(self.logs[metric], label=metric)

        plt.legend()

        plt.show()

    def save(self):
        os.makedirs(f'{self.repo}/{self.name}/{self.run_id}', exist_ok=True)
        with open(f'{self.repo}/{self.name}/{self.run_id}/data.json', 'w') as f:
            json.dump({
                'run_id': self.run_id,
                'start_time': self.start_time,
                'last_update': self.last_update,
                'flush_interval': self.flush_interval,
                'name': self.name,
                'tag': self.tag,
                'repo': self.repo,
                'params': self.params,
                'logs': self.logs
            }, f)

    def close(self):
        self.save()