"""Pinned llama.cpp process backend; no server endpoint or model download."""
import re
from .process import checked_file, run
from airon_adaptation.knowledge import SOURCE_COPY_INSTRUCTION
from airon_adaptation.integrity import Rejected

def generate_prompt(config, system, user, *, max_tokens=160):
    binary, model = checked_file(config["binary"]), checked_file(config["model"])
    if len(system)+len(user)>3500 or not 1<=max_tokens<=160: raise Rejected("Context policy exceeded")
    prompt = "<|im_start|>system\n"+system+"<|im_end|>\n<|im_start|>user\n"+user+"<|im_end|>\n<|im_start|>assistant\n"
    output = run([binary,"-m",model,"-p",prompt,"-n",str(max_tokens),"-c","1024","-t","2",
                  "--temp","0","--seed","56","--no-display-prompt","--no-conversation","--simple-io","--perf"],timeout=180)
    # Exclude prompt-evaluation speed: it is not generation throughput.
    speed = re.search(r"(?m)^.*?:\s+eval time\s*=.*?\(.*?,\s*([0-9.]+) tokens per second\)",output["stderr"])
    return {"text":output["stdout"],"measurement":output["measurement"],"backend_log":output["stderr"],
            "ttft_s":None,"tokens_per_second":float(speed.group(1)) if speed else None,
            "timing_note":"Whole-process timing; token streaming not measured"}

def llama_generate(config, question, source):
    if len(source)>1800 or len(question)>500: raise Rejected("Context policy exceeded")
    return generate_prompt(config,SOURCE_COPY_INSTRUCTION,"Question: "+question+"\nApproved source text:\n"+source)
