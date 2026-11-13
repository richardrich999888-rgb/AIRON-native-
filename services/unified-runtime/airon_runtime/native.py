"""Versioned process boundary. Native code and its ownership stay in AIP."""
import json
from pathlib import Path
from airon_adaptation.integrity import Rejected
from .process import checked_file, run

class Native:
    def __init__(self, provision):
        self.provision = provision

    def call(self, operation, params, actor):
        binary = checked_file(self.provision["bridge"])
        config = checked_file(self.provision["config"])
        identity = checked_file(self.provision["identities"][actor])
        response = run([binary,config,identity],data={"operation":operation,**params})
        value = json.loads(response["stdout"])
        if value.get("schema") != "syntriass-airon-bridge/v1":
            raise Rejected("Native contract version mismatch")
        return {**value, "measurement":response["measurement"]}

    def lifecycle(self, command, args):
        if command not in {"cap-propose","cap-validate","cap-approve","cap-activate","cap-rollback","cap-list","cap-history"}:
            raise Rejected("Lifecycle command outside contract")
        binary = checked_file(self.provision["cli"])
        config = checked_file(self.provision["config"])
        response = run([binary,command,"--config",config,*args])
        return [json.loads(line) for line in response["stdout"].splitlines() if line.strip()]
