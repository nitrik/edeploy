#!/usr/bin/env python
#
# Copyright (C) 2013 eNovance SAS <licensing@enovance.com>
#
# Author: Gaetan Trellu <gaetan.trellu@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import sys
import subprocess
import re

CMD_REPORT = "/opt/dell/srvadmin/bin/omreport"
CMD_CONFIG = "/opt/dell/srvadmin/bin/omconfig"

ID_REGEXP = re.compile('^ID(.*)[0-9]$')
NAME_REGEXP = re.compile('^Device(.*)')


def parse_ctrl_all_show(output):
    for line in output.split('\n'):
        res = ID_REGEXP.search(line)
        if res:
            res = res.group().split(':')

            return res[1].strip()


def parse_pdisk_show(output, diskid, getall):
    lst = []
    for line in output.split('\n'):
        res = ID_REGEXP.search(line)
        if res:
            res = res.group().split(':')
            res = res[1] + ':' + res[2] + ':' + res[3]
            lst.append(res.strip())
    if getall:
        return lst
    else:
        return lst[diskid]


def parse_vdisk_show(output):
    lst = []
    for line in output.split('\n'):
        res = ID_REGEXP.search(line)
        device = NAME_REGEXP.search(line)
        if res:
            res = res.group().split(':')
            lst.append(res[1].strip())
        if device:
            device = device.group().split(':')
            lst.append(device[1].strip())

    return lst


class Cli:
    def __init__(self, debug=False):
        self.debug = debug

    def _sendline(self, cmd):
        if self.debug:
            print cmd
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ret, err = process.communicate()
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ret, err = process.communicate()
	except:
	    ret = err
        return ret

    def ctrl_show(self):
        args = 'storage controller'
        cmdstorage = CMD_REPORT + ' ' + args

        return parse_ctrl_all_show(self._sendline(cmdstorage))


    def pdisk_show(self, controller, diskid, getall=False):
        args = 'storage pdisk controller=%s' % controller
        cmdstorage = CMD_REPORT + ' ' + args

        return parse_pdisk_show(self._sendline(cmdstorage), diskid, getall)


    def vdisk_create(self, controller, drives, raid):
        args = 'storage controller action=createvdisk controller=%s raid=%s size=max pdisk=%s readpolicy=ara' % (
        controller, raid, ','.join(drives))
        cmdstorage = CMD_CONFIG + ' ' + args
        self._sendline(cmdstorage)

	slot = self.ctrl_show()
        name = self.vdisk_show(slot)

        return name[-1]


    def vdisk_show(self, controller):
        args = 'storage vdisk controller=%s' % controller
        cmdstorage = CMD_REPORT + ' ' + args

        return parse_vdisk_show(self._sendline(cmdstorage))


    def vdisk_delete(self, controller, vdiskid):
        for vdisk in vdiskid:
            args = 'storage vdisk action=deletevdisk controller=%s vdisk=%s' % (controller, vdisk)
            cmdstorage = CMD_CONFIG + ' ' + args
            self._sendline(cmdstorage)


#cli = Cli(debug=True)
#slot = cli.ctrl_show()
#disks = [cli.pdisk_show(slot, 2), cli.pdisk_show(slot, 3)]
#cli.vdisk_create(slot, disks, 'r1')
#cli.vdisk_show(slot)
#cli.vdisk_delete(slot, cli.vdisk_show(slot))
#cli.pdisk_show(slot, 2, getall=True)

