import asyncio

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from typing import Dict, Union
from concurrent.futures import ThreadPoolExecutor

import os
from validator.prompting_protocol import PromptingProtocol
import uvicorn

class ValidatorProxy():
    def __init__(self, validator_session, port, authentication_tokens = [], approved_urls = ""):

        self.validator_session = validator_session
        self.port = port
        self.authentication_tokens = authentication_tokens

        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.app.add_api_route("/validator_proxy", self.forward, methods=["POST"], dependencies=[Depends(self.get_self)])

        self.start_server()


    def start_server(self):
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.executor.submit(uvicorn.run, self.app, host="0.0.0.0", port=self.port)

    def authenticate_token(self, authorization):
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(status_code=401, detail="Invalid authentication scheme")

            # Simple token validation (replace this with your actual validation logic)
            if token not in self.authentication_tokens:
                print("Only available tokens are:", self.authentication_tokens, flush=True)
                raise HTTPException(status_code=401, detail="Invalid token")

            return token
        except Exception as e:
            print("Exception occured in authenticating token", e, flush=True)
            raise HTTPException(status_code=401, detail="Error getting authentication token")

    def get_uids_info(self):
        return self.validator_session.uids_info.get_full_uids_info()

    async def forward(self, data: dict={}):

        self.authenticate_token(data["Authorization"])

        try:
            category = data.get("category", None)
            if category == "get_info":
                return JSONResponse(content={"status": "success", "result":self.get_uids_info()})

            else:
                payload = data.get("payload")
                uid = int(data.get("UID"))
                synapse = PromptingProtocol(prompt_input = payload)


                uid_to_axon = dict(zip([int(uid) for uid in self.validator_session.metagraph.uids],  self.validator_session.metagraph.axons))
                axon = uid_to_axon[int(uid)]
                task = asyncio.create_task(self.validator_session.dendrite.forward([axon], synapse, deserialize=True))
                await asyncio.gather(task)


                result = task.result()
                return JSONResponse(content={"status": "success", "result":result[0]})
        except Exception as e:
            print("Exception occured in proxy forward", e, flush=True)
            raise HTTPException(status_code=400, detail=str(e))


    async def get_self(self):
        return self
