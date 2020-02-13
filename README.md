
# High-Availability-Processes  
Implementation of client, proxy, and  server with high availability:  
`Fault-Tolerant Tuple Space Service`  
  
The specifications are in `specs.doc`  
this spec where written by my [Dr. Phil Pfeiffer](https://www.linkedin.com/in/philpfeiffer/).  
  
  
# Details  
  
CSCI 5150:  Phil Pfeiffer  
Software-based final exam – fault-tolerant tuple space service  
Terms:  As individuals or in pairs  
Due date: Monday, 10 December, close of business, with interviews to follow  
  
## Background:  
One reason for implementing a distributed system is to assure a service's _fault-tolerance_: i.e., its ability to operate after component failures.  One classic architecture for ensuring fault tolerance, the **_active-passive_** architecture, uses a second, **_hot-swap_** server to back up a primary server (Figure 1). This configuration operates as follows:  
- The primary (i.e., active) server, in normal operation,  
   - Receives and responds to all requests from client computers  
   - Relays all requests for updating the primary's internal state to the backup, which maintains a duplicate of the primary's internal state.  
- The primary and backup servers, in normal operation, monitor each other's status, using "heartbeat" messages.  
- If one of the servers detects that the other has failed:  
   - If the primary detects a failure of the backup  
      - It notifies an operator that a failure has occurred and keeps operating.  
      - The operator should then  
         - restore the backup  
         - initiate a procedure for resynchronizing its state with the primary server  
   - If the backup server detects a failure of the primary  
      - It triggers the computer-controlled switch,  rerouting of client requests from the failed primary to itself.  
      - It notifies an operator that a failure has occurred and keeps operating.  
      - The operator should then  
         - restore the primary, which becomes the backup  
         - initiate a procedure for resynchronizing its state with the primary  
  
This assignment asks you to implement a comparable configuration, using a proxy server in place of the "deadman" switch (Figure 2).  
  
## Requirements: The requirements for this assignment are divisible into requirements for   
- The service    
- Primary and backup servers;   
- Proxy server  
- Client application