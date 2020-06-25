# Adding your own transport to O.I.F.

This is a tutorial on adding additional, custom transport mechanisms to the O.I.F.

## Adding Transport to Docker Stack

> **NOTE:**  "orchestrator compose" link below is broken;
> need fix,

Open the [Orchestrator Compose file](orchestrator-compose.yaml) to add your transport to the stack. You can copy-paste either the `transport-https` or `transport-mqtt` images and replace it with your own transport's info. Read more on Docker Compose [here](https://docs.docker.com/compose/overview/).

Here is what our HTTPS transport looks like:

```yaml
transport-https:                                    # container name
    hostname: transport-https                       # hostname of container
    image: oif/transport:orchestrator-https         # image name
    build:
      context: ./orchestrator/transport/https       # location of dockerfile
      dockerfile: Dockerfile                        # dockerfile name
    working_dir: /opt/transport                     # directory internal to the image which it calls from
    env_file:
      - ./environment/queue.connect.env             # path to shared environment variables
    external_links:
      - queue                                       # link to internal buffer (used to send/receive commands internally within O.I.F.)
    ports:
      - 5000:5000                                   # port exposed for HTTP
    depends_on:
      - queue                                       # indicates that this container should wait for queue to exist before running
    entrypoint:
      - sh
      - dev_start.sh                                # indicates script used to start-up desired functionality within image
```

Once added to the compose, your transport will be brought up as a part of the docker-compose stack and be added to the stack's docker network.

## Adding port information to the O.I.F.

When a transport sends a command while residing on a [Docker Network](https://docs.docker.com/network/), the Docker Network will obscure the IP and Port such that it appears that the message came from the location of the Docker Stack and not the originating machine. To ensure that the response is able to return to the originating machine we need to send the IP and Port as a part of the headers. 

The IP can be set in the O.I.F. Admin Page > Global Preferences > Orchestrator Host. The default value is `127.0.0.1`.

The Port for each transport needs to be set in the data fixtures file [orchestrator.json](../orchestrator/core/orc_server/data/fixtures/orchestrator.json). (See example at bottom of this page.) The port is specified under orchestrator.protocol under the "fields" section once you have added your transport to the list of orchestator.protocols. 

## Listening to the Internal Buffer

> **NOTE:**  the links below for `sb_utils` and "view an
> example" return 404 on GH (at least in my fork); need to fix

The Orchestrator and Device routes messages to the correct transport by using an internal AMQP broker. This buffer is a structure that is a part of the O.I.F. for routing messages to the correct locations, but NOT a part of OpenC2 itself. Note that the port does not appear in the docker-compose file, because although the image utilizes default port 5672 for AMQP, the port is not exposed. The [sb_utils](../modules/utils/sb_utils/amqp_tools.py) module has a Consumer wrapper available for use to easily implement for your transport. You can view an example [here](../orchestrator/transport/https/https/https_transport.py) which looks like this:

```python
from sb_utils import Consumer

    print("Connecting to RabbitMQ...")
    try:
        consumer = Consumer(
            exchange="transport",
            routing_key="https",
            callbacks=[process_message])

    except Exception as error:
        print(error)
        consumer.shutdown()
```

### Listening to Orchestrator

As you can see the O.I.F. utilizes the convention of `exchange="transport"` and `routing_key=transportProtocolName`. Upon receiving a message, the consumer triggers a callback method. It is within this callback in which you will execute your own transport methods in order to send the OpenC2 Command in the desired protocol.

### Listening to the Actuator

To add the transport to the device side the process is the same, except it is listening and writes to the actuator (in the example of our demo actuators). 

They listen on `exchange="actuator"` and `routing_key=actuatorProfileName` (eg. OpenC2_ISR_Actuator_Profile) where the transports follow the same convention as on the orchestrator-side. When the device-transport receives a message from the transport on the orchestrator-side, it forwards it to the correct actuator by checking the actuator profile name and placing it onto the queue. After the actuator has processed the command and performed the desired action, it will send its response to the transport by sending it back to the orchestrator.

## Responding to the Orchestrator

To send a response/error message back to the Orchestrator, you will instantiate a Producer which can also be found in [sb_utils](modules/utils/sb_utils/amqp_tools.py). You can find a response example [here](../transport/https/https/main.py) which looks like this:

```python
from sb_utils import Producer

    producer = Producer()
    producer.publish(message=data, header=headers, exchange="orchestrator", routing_key="response")
```

* `message`: The response or error message to be sent.
* `header`: Any headers that were included in the response (such as CorrelationID for tracking the command).
* `exchange` and `routing_key`: The queue on the broker in which the Orchestrator is listening to.

## Utilizing and Formatting the Headers

### In order to make sure that we route all messages properly, the O.I.F. sends *custom* headers to each of the transports.

```json
{
    "source": 
    {
        "orchestratorID": "600661ba-1977-420e-8c21-92aff67b900f",
        "transport":
        {
            "type": "HTTPS", 
            "socket": "127.0.0.1:5000"
        }, 
        "correlationID": "79472795-81e8-4d94-b229-bee114bc7a7f", 
        "date": "Wed, 27 Feb 2019 16:12:23 UTC"
    }, 
    "destination": 
    [{
        "deviceID": "337917b5-9330-4107-94d2-5d7929019c23", 
        "socket": "127.0.0.1:5001", 
        "profile": ["openc2_isr_actuator_profile"], 
        "encoding": "json"
    }]
}
```

`Source`: Information for the O.I.F. orchestrator to allow responses back to it.  
* `orchestratorID`: Relates to this specific orchestrator so that actuators and transports can send responses appropriately.  
* `transport`: The desired transport mechanism as well the location to reach it.  
* `correlationID`: Identifier for this specific command being sent.  
* `date`: Timestamp for the created message.  

`Destination`: This is a list of locations in which to send the commands.  
* `deviceID`: Identifier for the device that contains the desired actuator.  
* `socket`: Location of the device which is ready to receive the command.  
* `profile`: The actuator profile name.  
* `encoding`: Format in which the message is encoded to.  

From this information, you are able to build the headers for your transport as needed to follow existing transport specs as closely as possible.

### Example OpenC2 Headers for HTTPS (constructed from the headers sent by the O.I.F.):

```json
{
    "Host": "openc2_isr_actuator_profile@127.0.0.1:5001", 
    "From": "600661ba-1977-420e-8c21-92aff67b900f@127.0.0.1:5000",
    "Content-type": "application/openc2-cmd+json;version=1.0",
    "X-Correlation-ID": "79472795-81e8-4d94-b229-bee114bc7a7f",
}
```

* `Host`: Composed of the actuator profile name of the destination actuator + socket where the actuator is listening.
* `From`: Composed of the OrchestratorID + socket where the orchestrator-side transport is listening.
* `Content-type`: The content type of the message.
* `X-Correlation-ID`: ID used to track the OpenC2 message with its response.

## Making the transport usable in the O.I.F. GUI

In order to have the transport that you have created selectable in the "Register Device" section of the GUI you will need to add it to the [fixtures file](../orchestrator/core/orc_server/data/fixtures/orchestrator.json) and add it as an additional `orchestrator.protocol`. The other transports look like this:

```json
  {
    "model": "orchestrator.protocol",
    "pk": 1,
    "fields": {
      "name": "HTTPS",
      "port": 5000
    }
  },
  {
    "model": "orchestrator.protocol",
    "pk": 2,
    "fields": {
      "name": "MQTT",
      "pub_sub": true,
      "port": 1883
    }
  }
```

* `pub_sub`: If the transport being added follows a publish/subscribe model and utilizes a broker (or similar) set `pub_sub` to true. This will allow multiple transports to have the same ip:port since they may be connecting to the same broker under different queue/exchange/topic/etc.
* `pk` (private key): Increment this value to the next unused integer of model orchestrator.protocol
* `name`: Set this value to the desired protocol name.
* `port`: This is the port in which your transport will be listening on, and receiving responses from.

