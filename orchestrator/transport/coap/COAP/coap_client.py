import json

from coapthon import defines
from coapthon.client.helperclient import HelperClient
from coapthon.messages.option import Option
from coapthon.utils import generate_random_token

from sb_utils import encode_msg, safe_cast, Consumer


class CoapClient(HelperClient):
    def post(self, path, payload, callback=None, timeout=5, no_response=False, **kwargs):
        """
        Perform a POST on a certain path.
        :param path: the path
        :param payload: the request payload
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = kwargs.pop("request", self.mk_request(defines.Codes.POST, path))
        request.payload = payload
        request.token = generate_random_token(2)
        request.version = 1

        if no_response:
            request.add_no_response()
            request.type = defines.Types["NON"]

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout)


def send_coap(body, message):
    """
    AMQP Callback when we receive a message from internal buffer to be published
    :param body: Contains the message to be sent.
    :param message: Contains data about the message as well as headers
    """
    # Set destination and build requests for multiple potential endpoints.
    for device in message.headers.get("destination", {}):
        host, port = device["socket"].split(":", 1)
        encoding = device["encoding"]

        # Check necessary headers exist
        if host and port and encoding:
            path = "transport"
            client = CoapClient(server=(host, safe_cast(port, int, 5683)))
            request = client.mk_request(defines.Codes.POST, path)
            response = client.post(
                path=path,
                payload=encode_msg(json.loads(body), encoding),
                request=build_request(request, message.headers.get("source", {}), device)
            )

            if response:
                print(f"Response from device: {response}")
            client.stop()
        else:
            # send error back to orch
            print(f"Error: not enough data - {host}, {port}, {encoding}")


def build_request(request, headers, device):
    """
    Helper method to organized required headers into the CoAP Request.
    :param request: Request being build
    :param headers: Data from AMQP message which contains data to forward OpenC2 Command.
    :param device:  Device specific data from headers sent by O.I.F.
    """
    orc_host, orc_port = headers["transport"]["socket"].split(":", 1)    # location of orchestrator-side CoAP server
    request.source = (orc_host, safe_cast(orc_port, int, 5683))

    dev_host, dev_port = device["socket"].split(":", 1)    # location of device-side CoAP server
    request.destination = (dev_host, safe_cast(dev_port, int, 5683))

    encoding = f"application/{device['encoding']}"         # Content Serialization
    request.content_type = defines.Content_types[encoding]   # using application/json, TODO: add define to openc2+json
    request.mid = int("0x" + headers["correlationID"], 16)   # 16-bit correlationID
    request.timestamp = headers["date"]                      # time message was sent from orchestrator

    # Add OIF-unique value used for routing to the desired actuator
    profile = Option()
    profile.number = 8
    profile.value = device.get("profile", "")[0]
    request.add_option(profile)

    source_socket = Option()
    source_socket.number = 3
    source_socket.value = headers["transport"]["socket"]
    request.add_option(source_socket)

    return request


if __name__ == "__main__":
    # Begin consuming messages from internal message queue
    try:
        consumer = Consumer(
            exchange="transport",
            routing_key="coap",
            callbacks=[send_coap]
        )
    except Exception as e:
        print(f"Consumer error: {e}")
        consumer.shutdown()
