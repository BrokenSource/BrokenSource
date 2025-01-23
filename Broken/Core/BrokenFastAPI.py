import asyncio
import json
import time
from base64 import b64encode
from typing import Annotated

import uvicorn
from attrs import Factory, define
from fastapi import FastAPI
from typer import Option

from Broken import (
    BrokenPlatform,
    BrokenWorker,
)

# ------------------------------------------------------------------------------------------------ #

class Hosts:
    LOOPBACK: str = "127.0.0.1"
    WILDCARD: str = "0.0.0.0"

# Wildcard isn't necessarily localhost on Windows, make it explicit
DEFAULT_HOST: str = (Hosts.WILDCARD if BrokenPlatform.OnUnix else Hosts.LOOPBACK)
DEFAULT_PORT: int = 8000

# ------------------------------------------------------------------------------------------------ #

HostType = Annotated[str, Option("--host", "-h",
    help="Target Hostname to run the server on")]

PortType = Annotated[int, Option("--port", "-p",
    help="Target Port to run the server on")]

WorkersType = Annotated[int, Option("--workers", "-w", min=1,
    help="Maximum number of simultaneous renders")]

QueueType = Annotated[int, Option("--queue", "-q", min=1,
    help="Maximum number of requests until 503 (back-pressure)")]

BlockType = Annotated[bool, Option("--block", "-b", " /--free", " /-f",
    help="Block the current thread until the server stops")]

# ------------------------------------------------------------------------------------------------ #

@define
class BrokenAPI:
    api: FastAPI = Factory(FastAPI)
    """The main FastAPI instance"""

    host: str = DEFAULT_HOST
    """Hostname currently being used by the server"""

    port: int = DEFAULT_PORT
    """Port currently being used by the server"""

    # -------------------------------------------|
    # Utilities

    @property
    def api_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def openapi(self) -> dict:
        return self.api.openapi()

    @property
    def openapi_json(self) -> str:
        return json.dumps(self.openapi, ensure_ascii=False)

    # -------------------------------------------|
    # Actions

    def launch(self,
        host: HostType=DEFAULT_HOST,
        port: PortType=DEFAULT_PORT,
        queue: QueueType=20,
        block: BlockType=True,
    ) -> None:
        """Serve an instance of the api"""
        self.host, self.port = (host, port)

        # Proxy async converter
        async def serve():
            await uvicorn.Server(uvicorn.Config(
                host=self.host, port=self.port,
                app=self.api, loop="uvloop",
                limit_concurrency=queue,
            )).serve()

        # Start the server
        BrokenWorker.thread(asyncio.run, serve())

        # Hold main thread
        while bool(block):
            time.sleep(1)

    # -------------------------------------------|
    # Cloud providers

    def runpod(self,
        workers: WorkersType=3,
        queue: QueueType=20,
    ) -> None:
        """Run a serverless instance at runpod.io"""
        import runpod

        # Use the cool features of the local server
        BrokenAPI.launch(**locals(), block=False)

        async def wrapper(config: dict) -> dict:
            response = (await self.render(config["input"]))

            # Convert video to base64 for json transportation
            if any(type in response.media_type for type in ("video", "image")):
                response.body = b64encode(response.body).decode("utf-8")

            return dict(
                status_code=response.status_code,
                media_type=response.media_type,
                headers=response.headers,
                content=response.body,
            )

        # Call the render route directly
        runpod.serverless.start(dict(
            handler=wrapper
        ))
