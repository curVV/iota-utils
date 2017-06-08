# iota-utils
**nodeq** - simple bash script for quickly viewing node info  

can also paste results to online paste bin  

POSIX compliant  

Uses jq for nice output. If jq is not installed, Python's json.tool module will be used.  


### install ###

Copy it to a location on your path for convenient access.  

Make it executable:

`chmod +x nodeq` 


### usage ###


`nodeq --help`  


```
Usage: nodeq command [command-arg] [options]

Commands
  1|getNodeInfo                   Get node info
  2|getNeighbors                  Get neighbor info
  3|addNeighbor <neighbor>        Add neighbor
  4|removeNeighbor <neighbor>     Remove neighbor

Options:
  --node-uri      Specify node uri
                  example: --node-uri=http://192.168.1.1:14600
                  (default: change it to your liking at top of this script)
  --basic-auth    Http basic auth credentials, if required by the node
                  example: --basic-auth=user:password
                  (default: change it to your liking at top of this script)
  --paste         Paste result to remote paste bin (dpaste)
  --paste-noob    Paste result to remote paste bin (dpaste)
                  Same as --paste but does not hide addresses and sets
                  expire to 'once off' (expires after first view)
  --help          Print this help message

Examples:
  Get neighbours from a specific (other than default) node:
      nodeq getNeighbors --node-uri=http://anoherhost:1700
  Using numeric alias/shortcut for getting default node's neighbours:
      nodeq 2
  Get default node info and paste results to paste bin:
      nodeq 1 --paste     (same as: nodeq getNodeInfo --paste)

```
