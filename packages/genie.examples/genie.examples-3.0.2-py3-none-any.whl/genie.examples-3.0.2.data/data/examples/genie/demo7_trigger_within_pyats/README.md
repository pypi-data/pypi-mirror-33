## demo7_trigger_within_pyats

# Introduction

This script demonstrates how to include `Genie` Triggers and Verifications
within any existing `pyATS` script.

Triggers and verifications are pyATS Testcase. Here's how to add them to any
pyATS script:

* Import the Trigger/Verification
* Create a class which inherits from this Triggers/Verification
* Add the decorator
* If its a verification, add an uid which is not used yet, and child variable like in the example.
* Add to the datafile information about this trigger. This information can be found in the Trigger datafile
  ($VIRTUAL_ENV/genie_yamls/sdk/yaml/<os>/trigger_datafile_<os>.yaml)

# Execution

This demo requires devices. There is 2 options on how to run this demo:

1) This demo is ready to be used with the VIRL devices. Please follow the guide
   <here> on how to boot the virtual devices.

2) Use your own devices. Please modify the testbed file and mapping_datafile.yaml
   with the devices' names and the corresponding IP addresses.

```
easypy job/demo7_trigger_within_pyats_job.py -testbed_file virl.yaml -datafile datafile.yaml
```

# Output

The log can be viewed in the file `logviewer`.

# What's next?

Go ahead and add to your existing pyATS script any Genie Triggers for better coverage!
