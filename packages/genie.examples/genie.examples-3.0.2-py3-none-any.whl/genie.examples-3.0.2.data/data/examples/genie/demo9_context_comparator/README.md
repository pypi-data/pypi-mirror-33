## demo9_context_comparator

# Introduction

This script demonstrates how to compare show commands information between two
contexts (cli/xml). It first sends a show command with cli, then do the same
with xml, and compares the fields to make sure they are equal.

# Execution

This demo requires devices. There is 2 options on how to run this demo:

1) This demo is ready to be used with the VIRL devices. Please follow the guide
   <here> on how to boot the virtual devices.

2) Use your own devices. Please modify the testbed file and mapping_datafile.yaml
   with the devices' names and the corresponding IP addresses.

```
easypy job/demo9_context_comparator_job.py -testbed_file virl.yaml
```

# Output

The log can be viewed in the file `logviewer`.
