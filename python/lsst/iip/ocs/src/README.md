# How to run OCS components

1.run `./AckSubscriber`, `./CommandListener`, `./EventSubscriber` in 3 different terminals. 

## Descriptions
* AckSubscriber listens to acks from DMCS and ack them back to OCS. 
* CommandListener listens to commands from OCS to DMCS relating to archiver, catchuparchiver and processingcluster. 
* EventSubscriber listens to events from OCS and forwards them to DMCS. 
