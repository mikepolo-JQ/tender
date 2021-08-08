import django

django.setup()

import pytest

from applications.chat.consumers import ChatConsumer
from channels.testing import WebsocketCommunicator



# @pytest.mark.asyncio
# async def test_consumer():
#     communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/testws/")
#     connected, subprotocol = await communicator.connect()
#     assert connected
#     # Test sending text
#     await communicator.send_json_to({
#         "content": "Hello, Mike!"
#     })
#     response = await communicator.receive_from()
#     # assert response == "hello"
#
#     print(response)
#     # Close
#     await communicator.disconnect()
