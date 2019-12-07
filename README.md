# High-Availability-Processes
Implementation of client, proxy, and  server with high availability:
`Fault-Tolerant Tuple Space Service`

=============================================================================

**CSCI 5150:  Phil Pfeiffer**

**Software-based final exam – fault-tolerant tuple space service**

**Terms:  As individuals or in pairs**

**Due date:   Monday, 10 December, close of business, with interviews to follow**

=============================================================================

**Background** :  One reason for implementing a distributed system is to assure a service&#39;s _fault-tolerance_: i.e., its ability to operate after component failures.  One classic architecture for ensuring fault tolerance, the **active-passive** architecture, uses a second, **hot-swap** server to back up a primary server (Figure 1).   This configuration operates as follows:

- .The primary (i.e., active) server, in normal operation,
  - .Receives and responds to all requests from client computers
  - .Relays all requests for updating the primary&#39;s internal state to the backup, which maintains a duplicate of the primary&#39;s internal state.
- .The primary and backup servers, in normal operation, monitor each other&#39;s status, using &quot;heartbeat&quot; messages.
- .If one of the servers detects that the other has failed,
  - .If the primary detects a failure of the backup
    - .It notifies an operator that a failure has occurred and keeps operating.
    - .The operator should then
      - .restore the backup
      - .initiate a procedure for resynchronizing its state with the primary server
  - .If the backup server detects a failure of the primary
    - .It triggers the computer-controlled switch,  rerouting of client requests from the failed primary to itself.
    - .It notifies an operator that a failure has occurred and keeps operating.
    - .The operator should then
      - .restore the primary, which becomes the backup
      - .initiate a procedure for resynchronizing its state with the primary

This assignment asks you to implement a comparable configuration, using a proxy server in place of the &quot;deadman&quot; switch (Figure 2).

**Requirements** :  The requirements for this assignment are divisible into requirements for the primary and backup servers; for the proxy server; and for client applications.

-
. **Functional requirements for the service.**
- .The service shall provide a database service in the form of a tuple space:  i.e.,
- .a collection of (key, value) pairs, where
- .keys and values are n-tuples of alphanumeric strings
- .the space has at most one value per key
- .together with four operators:
- . **GET** - given a ( **keyexp** , **valexp** ) pair,
- .if the ( **keyexp** , **valexp** ) pattern is malformed, return an empty list.

_Note_: assume [Python regular expression syntax](https://docs.python.org/3/library/re.html) for **keyexp** and **valexp**.

- .else, return all ( **key** , **value** ) pairs such that
- . **key** matches **keyexp**
- . **value** matches **valexp**
- . **PUT** -given a purported list of ( **key** , **value** ) pairs,
- .if the list is malformed, return an indication to this effect
- .else
- .for every pair such that
- . **key** and **value** are well-formed and
- . **key** is not yet present in the tuple space

add ( **key** , **value** ) to the tuple space

- .return all ( **key** , **value** ) pairs that could not be added to the tuple space
- . **POST** -given a purported list of ( **key** , **value** ) pairs,
- .if the list itself is malformed, return an indication to this effect
- .else
- .for every pair such that
- . **key** and **value** are well-formed and
- . **key** is not present in the tuple space

update the value associated with **key** to **value**

- .return  all ( **key** , **value** ) pairs that were not used to update the tuple space
- . **DELETE** - given a ( **keyexp** , **valexp** ) pair,
- .if the ( **keyexp** , **valexp** ) pattern is malformed, return an empty list.

_Note_: assume [Python regular expression syntax](https://docs.python.org/3/library/re.html) for **keyexp** and **valexp**.

- .otherwise
- .remove all ( **key** , **value** ) pairs from the tuple space such that
- . **key** matches **keyexp**
- . **value** matches **valexp**
- .return a list of all ( **key** , **value** ) pairs that were removed from the tuple space
- .The service shall respond to other operators with an indication that the operator is not implemented.
- .Requirements for the proxy server.
- .The proxy shall provide the tuple space service as a connection-oriented serve, using a TCP socket.
- .The proxy shall impose a predetermined limit on the number of concurrent clients it can serve.
- .Any clients that connect beyond this limit shall be sent a &quot;service refused&quot; message, and their connection immediately dropped.
- .The proxy shall use the primary to manage all client requests for service.
- .The proxy shall relay each client request to the primary
- .To disambiguate requests, the proxy shall include a connection indicator with each request. This indicator will identify the client that placed the request.
- .The proxy shall relay each of the primary&#39;s responses to the request&#39;s initiating client, in the order in which these responses are received from the primary.
- .Upon receiving each response from the primary, the proxy shall strip the connection indicator from the response and relay the rest of the response to the requesting client.
- .The proxy shall operate as follows:
- .on startup, the proxy shall
- .accept three command line arguments

1. a local SAP for receiving connections from clients
2. a local SAP for receiving connections from the primary
3. a local SAP for receiving shutdown commands

- .fail if any of the arguments are malformed

- .initialize the SAPs indicated by arguments 1, 2, and 3

- .if initialization fails, shut down

- .in steady state processing, the proxy shall
- .maintain
- .an (incoming) request-focused connection from the primary at argument 1, and
- .an (outgoing) shutdown connection with the primary, at a primary-specified SAP
- .when these connections are absent or broken, block to initiate each
- .incoming, request-focused connection first, followed by
- .the outgoing connection for primary shutdown

subject to a &quot;reasonable&quot; timeout

- .if either connection can&#39;t be initiated, shut down

- .maintain up to the maximum limit of connections with client processes
- .drop any clients that attempt to connect after this limit is reached
- .accept requests from clients,
- .associating each request with a connection number, and
- .queuing the request to send to the primary
- .relay enqueued requests from clients to the primary

- .if the attempt to relay a request fails, treat the failure as a broken connection failure, per above

- .accept responses to enqueued requests from the primary
- .discarding ill-formed responses and responses from clients that have disconnected
- .relaying responses to their initiators, stripping the connection number from the response
- .upon receiving a shutdown request on the shutdown SAP
- .relay the request to the primary

- .shut down

- .Requirements for the primary server.
- .The primary shall provide the tuple space service, using a TCP socket
- .The primary shall receive all requests for the service from the system&#39;s proxy.
- .The primary any request that fails to include a connection indicator - a proxy-provided identifier that the proxy will use to identify the client that originated the request
- .The primary shall
- .process each request, per the requirements for the tuple space service
- .update the backup in parallel with the processing of PUT, POST, and DELETE requests
- .respond to each request after processing it, returning the request&#39;s identifier, unchanged, as part of its response
- .The primary shall operate as follows:
- .n startup, the primary shall
- .accept seven command line arguments:

1. a local SAP for receiving shutdown commands
2. a remote SAP for obtaining requests from the proxy
3. a backup-local SAP for sending update requests to the backup
4. a primary-local SAP for receiving heartbeat messages from the backup
5. a value that, if not null, names a file to which to write the tuple space data on shutdown
6. a null value, to denote that this process is starting as the primary
7. a value that, if not null, names a file from which to initialize the tuple space data on startup

- .fail if any of the arguments are malformed

- .load its tuple space from argument 7, if that argument is not null

- .if initialization fails - i.e., the file is unreadable or its contents are malformed - fail

- .in its initial phase of operation, the primary shall
- .initialize the SAP indicated by argument 4

- .if initialization fails
  - .write the contents of the tuple space to the file named in argument 5, if any
  - .shut down

- .start the backup with seven arguments:
- .arguments 1-5 as above
- .argument 6 - a handle that can be used to kill the primary - here, the primary&#39;s process ID
- .argument 7 - a null value

- .if the backup can&#39;t be started
  - .write the current contents of the tuple space to the file named in argument 5, if any
  - .shut down

- .btain a connection from the backup, at the SAP indicated by argument 4

- .if the connection isn&#39;t obtained within a reasonable period of time
  - .write the current contents of the tuple space to the file named in argument 5, if any
  - .shut down

- .connect to the backup at the SAP indicated by argument 3

- . if the connection can&#39;t be established within a reasonable period of time
  - .write the current contents of the tuple space to the file named in argument 5, if any
  - .shut down

- .use a PUT initialize the backup&#39;s tuple space

- .if the initialization fails
  - .write the current  contents of the tuple space to the file named in argument 6, if any
  - .shut down

- .connect to the proxy at the (client request) SAPs indicated by argument 2, sending the (shutdown command) SAP to the proxy, as indicated by argument 1

- .if the connections can&#39;t be established within a reasonable period of time
  - .write the current contents of the tuple space to the file named in argument 5, if any
  - .shut down

- .obtain a connection from the proxy, at the (shutdown command) SAP indicated by argument 1

- .if the connection isn&#39;t obtained within a reasonable period of time
  - .write the current contents of the tuple space to the file named in argument 5, if any
  - .shut down

- .in its steady-state phase of operation, the primary shall
- .repeatedly accept and respond to requests from the proxy per service requirements: i.e.,

- .respond to GET, PUT, POST, and DELETE requests, per the system requirements
- .respond to other requests with a &quot;not implemented&quot; message, per the system requirements.
- .include each request&#39;s connection number in the response to that request.

- .periodically accept and respond to heartbeat messages from the backup

- .on proxy failure, self-failure, or a shutdown message from the proxy
  - .terminate the backup
  - .write the current contents of the tuple space to the file named in argument 5, if any
  - .shut down
- .on backup failure
  - .make a reasonable number of attempts to restart the backup, initializing its tuple space
  - .on failure of these attempts
    - .write the current contents of the tuple space to the file named in argument 5, if any
    - .shut down

- . **Requirements for the backup server.**
- .On startup, the backup shall

- .accept seven command line arguments:

1. an SAP - i.e., (IP, port) pair - for obtaining shutdown commands from the proxy
2. an SAP for obtaining requests from the proxy
3. an SAP for receiving update requests from the primary
4. an SAP for sending heartbeat messages to the primary
5. a handle on the primary - for this assignment, the primary process&#39;s ID
6. a value that, if not null, names a file to which to write the tuple space data on shutdown
7. a null value

- .fail with an appropriate error message if any of the arguments are malformed

- .initialize the SAP indicated by argument 3

- .fail if initialization fails

- .obtain a connection from the primary, at the SAP indicated by argument 3

- .fail if the connection isn&#39;t obtained within a reasonable period of time

- .use the connection from the primary to initialize its tuple space

- .fail if the initialization doesn&#39;t succeed

- .connect to the primary at the SAP indicated by argument 4

- .fail if the connection can&#39;t be established within a reasonable period of time

- .In steady-state operation, the backup shall

- .repeatedly accept PUT, POST, and DELETE requests from the primary
- .updating its state according to what the request specifies
- .returning no messages to the primary
- .periodically send heartbeat messages to and accept responses from the primary

- .on primary failure
  - .terminate the primary
  - .close the SAP named in argument 3
  - .become the primary
  - .enter the initial phase of primary operation

- . **Requirements for clients.**
- .Clients should be capable of
- .connecting to and disconnecting from the proxy&#39;s request and shutdown ports.
- .sending well-formed and malformed GET, PUT, POST, and DELETE requests to the proxy on the proxy&#39;s request port
- .sending unknown requests to the proxy on the proxy&#39;s request port
- .sending a shutdown request to the proxy server on the proxy&#39;s shutdown port

- .displaying proxy responses to its requests
- . **Non-functional requirements:**
- .Create your codes &quot;from scratch&quot;, feeling free to build on my code
- .The basic communications machinery that you&#39;ll need to use is in the examples in place;  I recommend using it, augmenting routines with timeout capability as reqired
- .Do NOT submit blocks of code downloaded wholesale from the Internet or copied from other sources.
- .Define all &quot;non-obvious&quot; constants in a block at the start of your codes, giving them non-obvious names.
- . **Make all variable names self-documenting.**
- . **Make all error messages self-documenting.**
- . **Make all communications-related operations timeout-based.**  Timeouts are an essential element of sound network programming; codes that lack them should be regarded as toy codes.
- . **If you multithread your logic,** as I recommend, **make all threads event-loop-based.  ** Loop-based control is essential for sound thread-based programming.  Threads, as a rule, should **never** be terminated arbitrarily by other threads.  Rather, they should terminate themselves in response to a change of state that requests their termination.
- . **Ask before deviating from the requirements given above**
- .Adhere to the basic design principles that underlie this architecture: i.e.,
- . **Direct all requests for tuple space processing go to the primary, via the proxy.**
- .Limit the proxy&#39;s knowledge of the service to the current primary.
- .Limit all heartbeat checking to message exchanges between the primary and the backup.
- .Do not deviate from the requirements given in red.
- .While I&#39;m sure you can improve on my logic in various ways, including the pseudocode given at the end of this assignment, be careful not to implement functionality that will further complicate a fairly complex assignment - at least, until you get the basic logic working.

**Deliverables** :  Your codes, along with

- .an explanation of what you failed to get to work - if you failed to get some of the required features to work
- .enough by way of test runs to show that the functionality that you believe works is indeed working
- .a half-hour interview during exam week where you and your partner (if you have one) explain your code&#39;s working

**Deployment-related recommendations:**

When running your codes, start them in the following order:

- .Start the proxy.
- .Start the primary.  The primary should then start the backup and connect to the proxy.
- .Start the client processes.

**Design-related recommendations:  **

- .By way of help, the following pages provide starter pseudocodes for the proxy and a combination primary/backup tuple space server - one that can flip from backup to primary at need.

- .The proxy code is K+2-threaded.  It uses
- .K threads to handle communications with the K clients
- .one thread to handle shutdown requests
- .a main thread to start processing and oversee the process&#39;s overall operation
- .The tuple space server pseudocode uses three threads:
- .one thread to handle heartbeat requests
- .one thread to handle shutdown requests
- .a main thread to start processing and oversee the process&#39;s overall operation

While I don&#39;t guarantee that the codes are perfect, I&#39;ve repeatedly reviewed the logic and my choice of names.   **In particular, note that the pseudocode control logic for every thread is event-loop based, with timeouts used to limit the time needed for each potentially blocking operation.**

- .Much of this assignment, I believe, will involve your
- .making a study of my code and
- .using appropriate data structures to juggle connections in the server.

I think you&#39;ll need

- .a dictionary to map connections to user IDs
- .dynamically generated inverses of this dictionary to map user IDs to connections

For the latter, you can find enough idioms for generating these on the Internet.

- .You&#39;ll need to define a protocol for structuring client requests.  A classic strategy for doing this is to treat each request as a string of the form

**requestType** \&lt; **separator payload** \&gt;

where

- . **requestType**  is the type for the request
- .\&lt; **separator payload** \&gt; is a request-type-dependent parameter, consisting of
- .a separator character that divides the request type ID from the payload
- .a string of characters (payload) that parameterizes the request type
- .**Be sure to use setsockopt() to set  SO\_REUSEADDR  to 1 (true) for all  SAPs  that are local to the primary, to ensure that SAP rebindings on primary failure are immediate, not delayed.**
- .For more on Python support for interactive input, see Python&#39;s **input()** function, in the builtins library.
- .For more on Python support for regular expression manipulation, see the Python library&#39;s **re** module - particularly **re.compile()** and _pattern_**.fullmatch()**, since the user-ID-specifying regular expression will need to be used to check every client-specified ID for well-formedness.

**.**.

Proxy process pseudocode

- .command line parameters
  - .\&lt;proxy\_from\_clients\_SAP\&gt;                SAP for receiving connections from clients
  - .\&lt;proxy\_from\_primary\_SAP\&gt;                SAP for receiving connections from the primary
  - .\&lt;proxy\_shutdown\_SAP\&gt;                SAP for receiving shutdown commands directed to proxy
- .program constants
  - .@max\_incoming\_client\_connections@        max number of incoming clients allowed - say, 5
  - .@incoming\_event\_timeout@        main routine timeout for polling for connection requests and shutdown commands - say, 2 seconds
  - .@connect\_with\_primary\_timeout@        main routine timeout for getting a connection from the primary - say, 60 seconds
  - .@get\_primary\_shutdown\_SAP\_timeout@        main routine timeout for getting the primary&#39;s shutdown SAP post-connection - say, 2 seconds?
  - .@incoming\_client\_request\_timeout@        client communication thread timeout for polling for incoming client request - say, 2 seconds?
  - .@send\_to\_primary\_timeout@        client communication thread timeout for relaying received message to primary - say, 2 seconds?
  - .@incoming\_primary\_response\_timeout@        client communication thread timeout for polling for primary responses - say, 2 seconds?
  - .@shutdown\_check\_timeout@        shutdown thread timeout for polling for incoming client request - say, 10 seconds?
- .proxy main thread

check parameters

**if ill-formed parameters detected, issue appropriate error message, then exit**

initialize \&lt;proxy\_shutdown\_SAP\&gt;

enable up to @max\_incoming\_client\_connections@ connections on \&lt;proxy\_shutdown\_SAP\&gt;

**on bind/listen sequence failure, issue appropriate error message, then exit**

launch **proxy-shutdown-thread**

**on thread launch failure, issue appropriate error message, then exit**

initialize \&lt;proxy\_from\_primary\_SAP\&gt;

enable 1 connection on \&lt;proxy\_from\_primary\_SAP\&gt;   ## need to open with SO\_REUSEADDR

on bind/listen sequence failure, issue appropriate error message, then exit

initialize main loop control variables

set &quot;I have failed&quot;, &quot;primary has failed&quot;, &quot;shut proxy down&quot;, &quot;primary initialized&quot;, &quot;client processing initialized&quot; to false

**while** not (&quot;I have failed&quot; or &quot;primary has failed&quot; or &quot;shut proxy down&quot;)

**if** not &quot;primary initialized&quot;

get connection on \&lt;proxy\_from\_primary\_SAP\&gt;, subject to @connect\_with\_primary\_timeout@

**on timeout, set &quot;primary has failed&quot; to true, continue**

receive \&lt;primary\_shutdown\_SAP\&gt; from primary, subject to @get\_primary\_shutdown\_SAP\_timeout@

**on timeout, set &quot;primary has failed&quot; to true, continue**

set &quot;primary initialized&quot; to true

**if** not &quot;client processing initialized&quot;

launch @max\_incoming\_client\_connections@ instances of **client communication thread**

**on thread launch failure, set &quot;I have failed&quot; to true, continue**

clear clients-\&gt;threads map     **# for relating responses to requests to clients that make them**

enable connections on \&lt;proxy\_from\_clients\_SAP\&gt;

**on bind/listen sequence failure, set &quot;primary has failed&quot; to true, continue**

**while** not (&quot;I have failed&quot; or &quot;primary has failed&quot; or &quot;shut proxy down&quot;) and &quot;primary initialized&quot;

use select to check for activity on \&lt;proxy\_from\_primary\_SAP\&gt; and \&lt;proxy\_from\_clients\_SAP\&gt;, subject to @incoming\_event\_timeout@

on timeout, continue

**if** \&lt;proxy\_from\_clients\_SAP\&gt; exception

**set &quot;I have failed&quot; to true, continue**

**if** \&lt;proxy\_from\_primary\_SAP\&gt; exception

close \&lt;proxy\_from\_primary\_SAP\&gt; connection

set &quot;primary initialized&quot; to false

continue

**if** \&lt;proxy\_from\_clients\_SAP\&gt; connect request

connect

determine if number of connected clients == @max\_incoming\_client\_connections@

**if** so         **# number of connected clients == @max\_incoming\_client\_connections@**

issue connection refused message

close connection

**else**           **# number of connected clients \&lt; @max\_incoming\_client\_connections@**

delegate processing on connection to a free **client communication thread** , updating client-\&gt;thread map

**if** \&lt;proxy\_from\_primary\_SAP\&gt; incoming message

determine identity of intended client

delegate message to intended thread for relay to client     **# need to check for proper client, due to recycling of threads**

shut down the proxy

send &quot;shut service down&quot; message to \&lt;proxy\_from\_primary\_SAP\&gt;

close \&lt;proxy\_from\_primary\_SAP\&gt;

close \&lt;proxy\_from\_clients\_SAP\&gt;

close \&lt;proxy\_shutdown\_SAP\&gt;

join with all client communication threads

- . **client communication threads**

**while** not (&quot;I have failed&quot; or &quot;shut proxy down&quot;)

set &quot;communicating with client&quot; to false

**while** not (&quot;I have failed&quot; or &quot;shut proxy down&quot; or &quot;communicating with client&quot;)

wait for a client connection handoff from the main thread, subject to @incoming\_client\_timeout@

**on timeout, continue**

set &quot;communicating with client&quot; to true

set &quot;client connection&quot; to connection obtained from the handoff from the main thread

**while** not (&quot;I have failed&quot; or &quot;shut proxy down&quot;) and &quot;communicating with client&quot;

set &quot;request-response phase&quot; to &quot;awaiting client request&quot;

**while** not (&quot;I have failed&quot; or &quot;primary has failed&quot; or &quot;shut proxy down&quot;) and &quot;communicating with client&quot;

check connection with client

on failure, set &quot;communicating with client&quot; to false, continue

determine request-response phase

**if**&quot;awaiting client request&quot;

receive message on &quot;client connection&quot;, subject to @incoming\_client\_request\_timeout@

on timeout, continue

on failure, set &quot;communicating with client&quot; to false, continue

enqueue the message

set &quot;request-response phase&quot; to &quot;awaiting send to primary&quot;

**else if**&quot;awaiting send to primary&quot;

acquire lock on \&lt;proxy\_from\_clients\_SAP\&gt;

**on failure, continue**

check for availability of send to \&lt;proxy\_from\_clients\_SAP\&gt;, subject to @send\_to\_primary\_timeout@

**on timeout, release lock on \&lt;proxy\_from\_clients\_SAP\&gt;, continue**

send request, adding client ID, to \&lt;proxy\_from\_clients\_SAP\&gt;

**on failure, release lock on \&lt;proxy\_from\_clients\_SAP\&gt;, set &quot;primary has failed&quot; to true, continue**

release lock on \&lt;proxy\_from\_clients\_SAP\&gt;

set &quot;request-response phase&quot; to &quot;awaiting primary response&quot;

**else      **** # awaiting primary response**

wait for a primary response from main, subject to @incoming\_primary\_response\_timeout@

on timeout, continue

on failure, set &quot;primary has failed&quot; to true, continue

send response, removing client ID, to &quot;client connection&quot;

on failure, set &quot;communicating with client&quot; to false, continue

set &quot;request-response phase&quot; to &quot;awaiting client request&quot;

close &quot;client connection&quot;

clear connection from clients-\&gt;threads map

- . **proxy-shutdown-thread**

**while** not (&quot;I have failed&quot; or &quot;primary has failed&quot; or &quot;shut proxy down&quot;)

receive message on \&lt;primary\_shutdown\_SAP\&gt;, subject to @shutdown\_check\_timeout@

on timeout, continue

**on failure, set &quot;I have failed&quot; to true, continue**

if message requests shutdown

**set &quot;shut proxy down&quot; to true**

**Tuple space server process pseudocode**

- .command line parameters
  - .\&lt;primary\_shutdown\_SAP\&gt;        SAP for receiving shutdown commands from the proxy
  - .\&lt;proxy\_from\_primary\_SAP\&gt;        SAP for receiving exchanging requests and responses with the proxy; should be same as proxy
  - .\&lt;backup\_from\_primary\_SAP\&gt;        SAP that the backup uses to receive commands from the primary
  - .\&lt;heartbeat\_SAP\&gt;        SAP that the primary uses to receive heartbeat messages from the backup
  - .\&lt;save\_data\_to\_this\_file\&gt;        if non-null, name of a file to which to write the program&#39;s tuple space data on shutdown
  - .\&lt;primary\_handle\&gt;        initially, null; thereafter, handle of primary
  - .\&lt;init\_data\_from\_this\_file\&gt;        initially, null or name of a file from which to initialize the tuple space; thereafter, null
- .internal parameters
  - .@control\_connection\_timeout@        control connection thread timeout for receives on \&lt;primary\_shutdown\_SAP\&gt; - say, 2 seconds?
  - .@incoming\_message\_timeout@        main timeout for receives on \&lt;proxy\_from\_primary\_SAP\&gt;, \&lt;backup\_from\_primary\_SAP\&gt; - say, 2 seconds?
  - .@heartbeat\_connection\_timeout@        heartbeat thread timeout for initial connection- say, 5 seconds?
  - .@heartbeat\_timeout@        heartbeat thread timeout for receives on \&lt;heartbeat\_SAP\&gt; - say, 1 second?
  - .@backup\_retry\_max@        number of retries allowed to start the backup - say, 5?
  - .@backup\_connection\_timeout@        heartbeat thread timeout for initial backup-primary connection- say, 5 seconds?
  - .@heartbeat\_retry\_max@        number of retries allowed for missed heartbeat messages - say, 5?
  - .@shutdown\_check\_timeout@        shutdown thread timeout for polling for incoming client request - say, 10 seconds?
- .server main thread

check parameters

if ill-formed parameters detected, issue appropriate error message, then exit

determine if \&lt;primary\_handle\&gt; is null

**if** \&lt;primary\_handle\&gt; is null         **# should only happen on initial execution**

set &quot;I am primary&quot; to true

set &quot;proxy connection active&quot;, &quot;primary shutdown connection active&quot; to false

enable connections (from backup) on \&lt;heartbeat\_SAP\&gt;

on bind/listen sequence failure, issue appropriate error message, then exit

determine if \&lt;init\_data\_from\_this\_file\&gt; parameter is non-null

**if** \&lt;init\_data\_from\_this\_file\&gt; parameter is non-null         **# should only happen on initial execution**

load tuple space from \&lt;init\_data\_from\_this\_file\&gt;

**on load failure, issue appropriate error message, then exit**

**else**     **# \&lt;init\_data\_from\_this\_file\&gt; parameter is absent**

clear tuple space

**else**   ** # \&lt;primary\_handle\&gt; is not null**

set &quot;I am primary&quot; to false

enable connections on \&lt;backup\_from\_primary\_SAP\&gt;   ## need to enable with SO\_REUSEADDR

on bind/listen sequence failure, issue appropriate error message, then exit

clear tuple space   **# will load tuple space from primary at later step in process**

initialize main loop control variables

set &quot;proxy has failed&quot;, &quot;I have failed&quot;, &quot;other server has failed&quot;, and &quot;shut service down&quot; to false

**while** not (&quot;proxy has failed&quot; or &quot;I have failed&quot; or &quot;shut service down&quot;)

**while** not (&quot;proxy has failed&quot; or &quot;I have failed&quot; or &quot;other server has failed&quot; or &quot;shut service down&quot;)

#  start attempt to initialize backup

set &quot;backup is initialized&quot; to false

**while** not (&quot;other server has failed&quot; or &quot;I have failed&quot; or &quot;backup is initialized&quot;)

determine if &quot;I am primary&quot;

**#  treat all failures to initialize backup as backup failures**

if &quot;I am primary&quot;

set &quot;backup launch retry count&quot; to 0

determine if &quot;backup launch retry count&quot; \&lt; @backup\_retry\_max@

**if &quot;backup launch retry count&quot; == @backup\_retry\_max@**

**set &quot;other server has failed&quot; to true, continue**

start a copy of this process--i.e., the backup process--with

\&lt;primary\_shutdown\_SAP\&gt;, \&lt;proxy\_from\_primary\_SAP\&gt;, \&lt;backup\_from\_primary\_SAP\&gt;, \&lt;heartbeat\_SAP\&gt;, null,
this process&#39;s handle, \&lt;save\_data\_to\_this\_file\&gt;

**on launch failure, increment retry count, continue**

set &quot;backup handle&quot; to ID of new process

acquire connection from \&lt;heartbeat\_SAP\&gt;, subject to @heartbeat\_connection\_timeout@

**on timeout, kill &quot;backup handle&quot;, increment retry count, continue**

connect to \&lt;backup\_from\_primary\_SAP\&gt;

**on timeout, kill &quot;backup handle&quot;, increment retry count, continue**

PUT contents of tuple space to \&lt;backup\_from\_primary\_SAP\&gt;

**on failure, kill &quot;backup handle&quot;, increment retry count, continue**

set &quot;backup is initialized&quot; to true

**else**   ** #  I&#39;m the backup**

enable connections (from primary) on \&lt;heartbeat\_SAP\&gt;

**on bind/listen sequence failure,** s **et &quot;I have failed&quot; to true, continue**

connect to \&lt;heartbeat\_SAP\&gt;, subject to @heartbeat\_connection\_timeout@

**on connection timeout,** s **et &quot;I have failed&quot; to true, continue**

acquire connection on \&lt;backup\_from\_primary\_SAP\&gt;, subject to @backup\_connection\_timeout@

**on connection timeout,** s **et &quot;I have failed&quot; to true, continue**

receive contents of tuple space on \&lt;backup\_from\_primary\_SAP\&gt;

**on receive failure or timeout,** s **et &quot;I have failed&quot; to true, continue**

set &quot;backup is initialized&quot; to true

**if**&quot;I have failed&quot; or &quot;other server has failed&quot;

continue

**#  start steady-state communications**

determine if &quot;I am primary&quot;

**if**&quot;I am primary&quot;

launch **other-checks-me heartbeat thread**

**on thread launch failure,** s **et &quot;I have failed&quot; to true, continue**

**if** not &quot;proxy connection active&quot;

connect to \&lt;proxy\_from\_primary\_SAP\&gt;

**on connection failure,** s **et &quot;proxy has failed&quot; to true, continue**

send \&lt;primary\_shutdown\_SAP\&gt; to \&lt;proxy\_from\_primary\_SAP\&gt;

**on send failure, set &quot;proxy has failed&quot; to true, continue**

**if** not &quot;primary shutdown connection active&quot;

enable connections (from backup) on \&lt;primary\_shutdown\_SAP\&gt;

**on bind/listen sequence failure,** s **et &quot;I have failed&quot; to true, continue**

launch **primary-shutdown-thread**

**on thread launch failure,** s **et &quot;I have failed&quot; to true, continue**

set &quot;primary shutdown connection active&quot; to true

**else**   **#  I&#39;m the backup**

launch **I-check-other heartbeat thread**

**on thread launch failure,** s **et &quot;I have failed&quot; to true, continue**

while not (&quot;proxy has failed&quot; or &quot;I have failed&quot; or &quot;other server has failed&quot; or &quot;shut service down&quot;)

determine if &quot;I am primary&quot;

**if**&quot;I am primary&quot;

receive message on \&lt;proxy\_from\_primary\_SAP\&gt;, subject to @incoming\_message\_timeout@

on timeout, continue

**on receive failure, set &quot;proxy has failed&quot; to true, continue**

send message, if PUT, POST, or DELETE to \&lt;backup\_from\_primary\_SAP\&gt;

**on send failure, set &quot;other server has failed&quot; to true, continue**

process message, updating tuple space

**else**   **#  I&#39;m the backup**

receive message on \&lt;backup\_from\_primary\_SAP\&gt;, subject to @incoming\_message\_timeout@

on timeout, continue

**on receive failure, set &quot;other server has failed&quot; to true, continue**

process message, updating tuple space

**#  something failed - ideally, it&#39;s the primary or backup**

join with heartbeat thread

close connection to \&lt;heartbeat\_SAP\&gt;

close connection to \&lt;backup\_from\_primary\_SAP\&gt;

**if**&quot;other server has failed&quot;

kill \&lt;primary\_handle\&gt;

#  if the primary has failed, hot swap the primary

**if** not &quot;I have failed&quot;

**if** not &quot;I am primary&quot;

set &quot;proxy connection active&quot; to false

set &quot;I am primary&quot; to true

**#  something major has failed - either the proxy failed, or I failed, or we have a shutdown request to process**

determine if &quot;I am primary&quot;

**if**&quot;I am primary&quot;

**if** not &quot;proxy has failed&quot; and &quot;proxy connection active&quot;

close connection to \&lt;proxy\_from\_primary\_SAP\&gt;

join with primary-shutdown-thread

**if** \&lt;save\_data\_to\_this\_file\&gt; not null

write tuple space to \&lt;save\_data\_to\_this\_file\&gt;

**else**     **# I&#39;m the backup**

**if**&quot;other server has failed&quot;

**if** \&lt;save\_data\_to\_this\_file\&gt; not null

write tuple space to \&lt;save\_data\_to\_this\_file\&gt;

- .other-checks-me heartbeat thread

while not (&quot;proxy has failed&quot; or &quot;I have failed&quot; or &quot;other server has failed&quot; or &quot;shut service down&quot;)

set &quot;heartbeat retry count&quot; to 0

while not (&quot;proxy has failed&quot; or &quot;I have failed&quot; or &quot;other server has failed&quot; or &quot;shut service down&quot;)

receive message on \&lt;heartbeat\_SAP\&gt;, subject to @heartbeat\_timeout@

on timeout

increment &quot;heartbeat retry count&quot;

if &quot;heartbeat retry count&quot; == @heartbeat\_retry\_max@

**set &quot;other server has failed&quot; to true, continue**

**on failure, set &quot;other server has failed&quot; to true, continue**

reply on \&lt;heartbeat\_SAP\&gt;

on failure, set &quot;other server has failed&quot; to true, continue

set &quot;heartbeat retry count&quot; to 0

- .I-check-other heartbeat thread

while not (&quot;proxy has failed&quot; or &quot;I have failed&quot; or &quot;other server has failed&quot; or &quot;shut service down&quot;)

set &quot;heartbeat retry count&quot; to 0

while not (&quot;proxy has failed&quot; or &quot;I have failed&quot; or &quot;other server has failed&quot; or &quot;shut service down&quot;)

send message to \&lt;heartbeat\_SAP\&gt;

on failure, set &quot;other server has failed&quot; to true, continue

receive reply on \&lt;heartbeat\_SAP\&gt;, subject to @heartbeat\_timeout@@

on timeout

increment &quot;heartbeat retry count&quot;

if &quot;heartbeat retry count&quot; == @heartbeat\_retry\_max@

set &quot;other server has failed&quot; to true, continue

on failure, set &quot;other server has failed&quot; to true, continue

set &quot;heartbeat retry count&quot; to 0

- . **primary-shutdown-thread**

**while** not (&quot;proxy has failed&#39; or &quot;I have failed&quot; or &quot;shut service down&quot;)

receive message on \&lt;primary\_shutdown\_SAP\&gt;, subject to @shutdown\_check\_timeout@

on timeout, continue

**on failure, set &quot;proxy has failed&quot; to true, continue**

if message requests shutdown

**set &quot;shut service down&quot; to true**