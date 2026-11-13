"""Pinned llama.cpp process backend; no server endpoint or model download."""
import re
from .process import checked_file, run
from airon_adaptation.knowledge import SOURCE_COPY_INSTRUCTION
from airon_adaptation.integrity import Rejected

def llama_generate(config, question, source):
    binary, model = checked_file(config["binary"]), checked_file(config["model"])
    if len(source)>1800 or len(question)>500: raise Rejected("Context policy exceeded")
    prompt = "<|im_start|>system\n"+SOURCE_COPY_INSTRUCTION+"<|im_end|>\n<|im_start|>user\nQuestion: "+question+"\nApproved source text:\n"+source+"<|im_end|>\n<|im_start|>assistant\n"
    output = run([binary,"-m",model,"-p",prompt,"-n","160","-c","1024","-t","2",
                  "--temp","0","--seed","56","--no-display-prompt","--no-conversation","--simple-io","--perf"],timeout=180)
    speed = re.search(r"eval time\s*=.*?\(.*?,\s*([0-9.]+) tokens per second\)",output["stderr"])
    return {"text":output["stdout"],"measurement":output["measurement"],"backend_log":output["stderr"],
            "ttft_s":None,"tokens_per_second":float(speed.group(1)) if speed else None,
            "timing_note":"Whole-process timing; token streaming not measured"}
