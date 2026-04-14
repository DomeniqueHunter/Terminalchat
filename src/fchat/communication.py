from .api import get_ticket
from .opcodes import Opcode as opcode

import json
import websockets.client
import asyncio
from collections import deque
from typing import Deque, Optional, Tuple

COMM_ERROR = "__ERROR"


def prettify(op:str="", message:str="") -> tuple:
    return op, message


class Communication:

    def __init__(self, config:dict) -> None:
        self.config = config
        self.connection = None

        self._send_queue: Deque[Tuple[str, dict | None]] = deque()
        self._queue_condition = asyncio.Condition()
        self._sender_task: Optional[asyncio.Task] = None

        self._recv_queue: Deque[str] = deque()
        self._recv_condition = asyncio.Condition()
        self._receiver_task: Optional[asyncio.Task] = None

    async def identify(self) -> None:
        data = {
            "method": "ticket",
            "ticket": await self.get_api_ticket(),
            "account": str(self.config.get("account")),
            "character": str(self.config.get("character")),
            "cname": "Terminal Chat Client",
            "cversion": "0.0.1",
        }

        await self.message(opcode.IDENTIFY, data)
        await self.read()

    async def connect(self) -> None:
        uri = self.config.get("protocol") + self.config.get("server") + self.config.get("endpoint")

        try:
            self.connection = await websockets.client.connect(uri)
            print(f"\nConnected to: {uri} - {self.status()}")
            return True

        except Exception as e:
            print(f"\nCould not connect to: {uri}")
            print(f"error: {e}")
            self.connection = None

        return False

    async def start_sender(self) -> None:
        if self._sender_task is None:
            self._sender_task = asyncio.create_task(self._send_loop())

    async def start_receiver(self) -> None:
        if self._receiver_task is None:
            self._receiver_task = asyncio.create_task(self._recv_loop())

    async def message(self, opcode: str, data: dict | None=None) -> None:
        async with self._queue_condition:
            self._send_queue.append((opcode, data))
            self._queue_condition.notify()

    async def priority_message(self, opcode: str, data: dict | None=None) -> None:
        async with self._queue_condition:
            self._send_queue.appendleft((opcode, data))
            self._queue_condition.notify()

    async def _send_message(self, opcode: str, data: dict | None=None) -> None:
        try:
            if data:
                await self.connection.send(f"{opcode} {json.dumps(data)}")
            else:
                await self.connection.send(opcode)

        except Exception as e:
            print("could not send data to server")
            print(e)

    async def read(self) -> str | None:
        try:
            return await self.connection.recv()

        except Exception as e:
            # print("could not read from stream")
            # print(e)
            return f"{COMM_ERROR} could not read from stream"

    async def receive(self) -> tuple[str, str]:
        try:
            async with self._recv_condition:
                while not self._recv_queue:
                    await self._recv_condition.wait()

                return prettify(*self._recv_queue.popleft())

        except Exception as e:
            # print(f"Connection Error: {e}")
            return COMM_ERROR, "Connection closed"

    async def get_api_ticket(self) -> str:
        return await get_ticket(self.config.get("account"), self.config.get("password"))

    def status(self) -> str:
        return self.connection.state.name

    async def _send_loop(self) -> None:
        while True:
            async with self._queue_condition:
                while not self._send_queue:
                    await self._queue_condition.wait()

                op, data = self._send_queue.popleft()

            await self._send_message(op, data)
            await asyncio.sleep(1.0)

    async def _recv_loop(self) -> None:
        while True:
            message_str = await self.read()
            try:
                data = message_str.split(" ", 1)

            except Exception as e:
                print(f"could not split message: {message_str}")
                print(e)
                data = (COMM_ERROR, "")

            async with self._recv_condition:
                if data[0] == opcode.PING:
                    self._recv_queue.appendleft(data)
                else:
                    self._recv_queue.append(data)
                self._recv_condition.notify()

    async def stop(self) -> None:
        # Cancel sender task
        if self._sender_task is not None:
            self._sender_task.cancel()
            try:
                await self._sender_task
            except asyncio.CancelledError:
                pass
            self._sender_task = None

        # Cancel receiver task
        if self._receiver_task is not None:
            self._receiver_task.cancel()
            try:
                await self._receiver_task
            except asyncio.CancelledError:
                pass
            self._receiver_task = None

        # Close WebSocket connection immediately
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

        # Clear queues
        self._send_queue.clear()
        self._recv_queue.clear()
