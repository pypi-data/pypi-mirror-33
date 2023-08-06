# coding=utf-8


import time
import json
from airtest_hunter import AirtestHunter, open_platform
from poco.drivers.netease.internal import NeteasePoco

from pocounit.case import PocoTestCase
from airtest.core.api import connect_device, device as current_device
from poco.drivers.android.uiautomation import AndroidUiautomationPoco


class Case(PocoTestCase):
    @classmethod
    def setUpClass(cls):
        super(Case, cls).setUpClass()
        if not current_device():
            connect_device('Android:///')

    def runTest(self):
        from poco.drivers.cocosjs import CocosJsPoco
        poco = CocosJsPoco()
        for n in poco():
            print(n.get_name())



from poco.utils.simplerpc.rpcclient import RpcClient
from poco.utils.simplerpc.transport.ws import WebSocketClient
# conn = WebSocketClient('ws://{}:{}'.format('10.254.49.179', 5003))
# c = RpcClient(conn)
# c.connect()
#
# cb = c.call('Dump', True)
# ret, err = cb.wait(timeout=10)
# print(ret, err)
# time.sleep(5)

from airtest.core.api import connect_device
from poco.utils.track import track_sampling, MotionTrack, MotionTrackBatch
from poco.utils.airtest.input import AirtestInput
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from poco.drivers.cocosjs import CocosJsPoco
from poco.drivers.unity3d.unity3d_poco import UnityPoco
from poco.utils.device import VirtualDevice


poco = UnityPoco(unity_editor=True)

# dev = connect_device('Android:///')
# dev = VirtualDevice('10.254.49.179')
# poco = CocosJsPoco('ws://:', dev)

for n in poco():
    print(n.get_name())

mt0 = MotionTrack()
mt1 = MotionTrack()
mt2 = MotionTrack()
mt0.start([0.5, 0.5]).move([0.2, 0.5]).move([0.5, 0.5]).hold(1)
mt1.start([0.5, 0.6]).move([0.2, 0.6]).hold(1).move([0.5, 0.6])
mt2.hold(1).start([0.5, 0.4]).move([0.2, 0.4]).move([0.5, 0.4])
poco.apply_motion_tracks([mt0, mt1, mt2])



connect_device('Android:///')
poco = AndroidUiautomationPoco(use_airtest_input=True)
poco('2333中文', text='另一个中文').click()

#
# meb = MotionTrackBatch([mt1, mt])
# for e in meb.discretize():
#     print e
# print len(meb.discretize())
# poco.apply_motion_tracks([mt1, mt])

time.sleep(4)

