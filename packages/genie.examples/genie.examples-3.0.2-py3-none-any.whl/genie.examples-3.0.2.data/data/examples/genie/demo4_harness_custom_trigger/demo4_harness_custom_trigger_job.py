'''demo4_harness_custom_trigger_job.py

Please read the README file.
'''

#
# optional author information
#
__author__ = 'Cisco Systems Inc.'
__copyright__ = 'Copyright (c) 2018, Cisco Systems Inc.'
__contact__ = ['pyats-support-ext@cisco.com']
__date__= 'April 2018'

#
# import block
#
import os

from ats.datastructures.logic import And, Not, Or
from genie.harness.main import gRun

def main():
    test_path = os.path.dirname(os.path.abspath(__file__))

    gRun(trigger_datafile=os.path.join(test_path, 'trigger_datafile_demo.yaml'), 
         verification_datafile=os.path.join(os.environ['VIRTUAL_ENV'], 'genie_yamls/nxos/verification_datafile_nxos.yaml'),
         mapping_datafile=os.path.join(test_path, 'mapping_datafile.yaml'),
         pts_features=['platform', 'bgp', 'interface'],
         #pts_features=['bgp', 'interface'],
         pts_datafile=os.path.join(os.environ['VIRTUAL_ENV'], 'genie_yamls/pts_datafile.yaml'),
         verification_uids=Or('Verify_IpInterfaceBrief', 'Verify_IpRoute_vrf_all'),
         trigger_uids=Or('TriggerUnconfigConfigBgp.uut', 'TriggerShutNoShutBgpNeighbors', 'TriggerModifyLoopbackInterfaceIp.uut', 'TriggerShutNoShutEthernetInterface', 'TriggerClearArpVrfAllForceDelete'))
