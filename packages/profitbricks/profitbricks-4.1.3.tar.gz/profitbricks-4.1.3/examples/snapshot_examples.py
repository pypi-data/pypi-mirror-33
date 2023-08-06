#!/usr/bin/python3

# Copyright 2015-2017 ProfitBricks GmbH
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

"""List Snapshots
"""

from __future__ import print_function

from profitbricks.client import ProfitBricksService

client = ProfitBricksService(
    username='username', password='password')

snapshots = client.list_snapshots()

for s in snapshots['items']:
    print(s['properties']['name'])

"""Get Snapshot
"""
from profitbricks.client import ProfitBricksService  # noqa

snapshot_id = '7df81087-5835-41c6-a10b-3e098593bba4'

client = ProfitBricksService(
    username='username', password='password')

snapshot = client.get_snapshot(
    snapshot_id=snapshot_id)

"""
Update Snapshot

Valid snapshot parameters are:

* name (str)
* description (str)
* licence_type (one of 'LINUX', 'WINDOWS' or 'UNKNOWN')
* cpu_hot_plug (bool)
* ram_hot_plug (bool)
* nic_hot_plug (bool)
* nic_hot_unplug (bool)
* disc_virtio_hot_plug (bool)
* disc_virtio_hot_unplug (bool)
* disc_scsi_hot_plug (bool)
* disc_scsi_hot_unplug (bool)

"""
from profitbricks.client import ProfitBricksService  # noqa

client = ProfitBricksService(
    username='username', password='password')

snapshot_id = 'd084aa0a-f9ab-41d5-9316-18163bc416ef'
image = client.update_snapshot(
    snapshot_id,
    name='New name',
    description="Backup of volume XYZ",
    licence_type='LINUX',
    cpu_hot_plug=True,
    ram_hot_plug=True,
    nic_hot_plug=True,
    nic_hot_unplug=True,
    disc_virtio_hot_plug=True,
    disc_virtio_hot_unplug=True)

"""Remove Snapshot
"""

from profitbricks.client import ProfitBricksService  # noqa

snapshot_id = '7df81087-5835-41c6-a10b-3e098593bba4'

client = ProfitBricksService(
    username='username', password='password')

snapshot = client.delete_snapshot(
    snapshot_id=snapshot_id)
