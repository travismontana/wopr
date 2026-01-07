# Copyright 2026 Bob Bomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from celery import Celery
from celery.schedules import crontab

app = Celery('celery_app', broker='redis://localhost:6379/0')
app.conf.update(
    result_backend='redis://localhost:6379/0',
    beat_schedule={
        'add-every-30-seconds': {
            'task': 'tasks.add',
            'schedule': 10.0, # run every 10 seconds
            'args': (10, 10)
        },
        'multiply-at-noon': {
            'task': 'tasks.multiply',
            'schedule': crontab(hour='12', minute='6'),
            'args': (4, 5)
        }
    },
    include=['tasks']
)