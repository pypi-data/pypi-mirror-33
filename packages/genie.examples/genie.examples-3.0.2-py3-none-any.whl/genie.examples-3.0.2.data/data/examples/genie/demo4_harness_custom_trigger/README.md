## demo4_harness_custom_trigger

# Introduction

This script demonstrates how to add your own `Trigger` to execute with existing
triggers. A trigger is a pyATS testcase which test some specific action. Look
inside the file `trigger.py`. Once created, the python path of the trigger must
be added to the `trigger_datafile_demo.yaml`.  Lastly, the
`demo4_harness_custom_trigger_job.py` was modified to add the new trigger to the
`trigger_uids`.

# Execution

This demo requires devices. There is 2 options on how to run this demo:

1) This demo is ready to be used with the VIRL devices. Please follow the guide
   <here> on how to boot the virtual devices.

2) Use your own devices. Please modify the testbed file and mapping_datafile.yaml
   with the devices' names and the corresponding IP addresses.

```
easypy demo4_harness_custom_trigger_job.py -testbed_file virl.yaml
```

# Output

The log can be viewed in the file `logviewer`.

# What's next?

After these 4 demos, you are now ready to run on your own Testbed, select a
combination of triggers and verificaitons and start your testing!

Move on to the next demo `demo5_robot` to learn how to use Genie and pyATS with
RobotFramework!
