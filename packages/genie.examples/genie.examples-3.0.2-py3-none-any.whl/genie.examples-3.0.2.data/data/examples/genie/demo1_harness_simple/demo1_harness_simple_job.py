'''demo1_genie_harness_job.py

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

    # Provide Trigger datafile
    # The mapping datafile is mandatory
    # Trigger_uids limit which test to execute
    gRun(trigger_datafile=os.path.join(os.environ['VIRTUAL_ENV'], 'genie_yamls/nxos/trigger_datafile_nxos.yaml'),
         mapping_datafile=os.path.join(test_path, 'mapping_datafile.yaml'),
         trigger_uids=Or('TriggerSleep'))
