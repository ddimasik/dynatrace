In general it works so:

- Each service during startup uses initContainer in order to put Dynatrace OneAgent distribution into main container' file system.
- Then, main container loads Dynatrace OneAgent library (by using env var LD_PRELOAD), it allows Dynatrace OneAgent to intercept system calls for monitoring purposes.
- And finally Dynatrace OneAgent uses env vars of the kind DT_* in order to connect to monitoring servers and transfers monitoring data.

In order to get service' dc.yaml with dynatrace configuration you should take any dc.yaml and patch it with script "add_oneagent.py". Here you recieve patched yaml in stdout:

 add_oneagent.py  dc.yaml

also you can patch file in place by: 

 add_oneagent.py --in-place  /path/to/dc.yaml

And after patching dc.yaml can be "kubectl applied" on kubernetes as usual.
