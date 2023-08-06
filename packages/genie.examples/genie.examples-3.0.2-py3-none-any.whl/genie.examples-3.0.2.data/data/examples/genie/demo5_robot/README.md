## demo5_robot

# Introduction

`RobotFramework` is an opensource test automation framework which provides automation,
without having to write code. It is `Keyword` driven. Libraries provide
Keywords to interact. `Genie` and `pyATS` provide keywords, to execute
Triggers and Testcases, parse commands, learn device features and many more.  It also uses
`Genie` `Operational` object, to verify if we have a right amount of Routes, up
interfaces, etc. 

# Execution

This demo requires devices. There is 2 options on how to run this demo:

1) This demo is ready to be used with the VIRL devices. Please follow the guide
   <here> on how to boot the virtual devices.

2) Use your own devices. Please modify the testbed file and mapping_datafile.yaml
   with the devices' names and the corresponding IP addresses.

Make sure you have robotframework installed

```
pip install robotframework
```

```
<open the demo5.robot file, and modify the testbed variable to point to your testbed file>
robot demo5.robot
```

# Output

The log can be viewed in the log.html

# What's next?

Move on to the next demo `demo6_config_ops` to learn how Genie use
Configuration and Operational objects to drive the device configuration and
operational state.
