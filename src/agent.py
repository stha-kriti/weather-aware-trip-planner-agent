"""Trip planner agent: a plain tool-calling loop on Azure OpenAI, no framework."""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from llm import deployment_name, make_client
from tools import TOOLS, run_tool

PROMPT = (Path(__file__).parent / "prompt.md").read_text(encoding="utf-8")


def run(request: str, client=None, model: str | None = None, max_steps: int = 6) -> str:
    client = client or make_client()
    model = model or deployment_name()
    system = PROMPT.replace("{today}", date.today().isoformat())
    messages = [{"role": "system", "content": system}, {"role": "user", "content": request}]

    for step in range(1, max_steps + 1):
        msg = client.chat.completions.create(model=model, messages=messages, tools=TOOLS).choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            return msg.content
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            print(f"[step {step}] {call.function.name}({args})", file=sys.stderr)
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": run_tool(call.function.name, args)})

    # Step budget used up: force a final answer instead of looping forever.
    messages.append({"role": "user", "content": "Step limit reached. Write the final answer now."})
    return client.chat.completions.create(model=model, messages=messages).choices[0].message.content


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Plan a short city trip around the forecast")
    parser.add_argument("request", help="Either a request in quotes or a path to a text file")
    parser.add_argument("-o", "--output", default="out/plan.md")
    args = parser.parse_args()

    source = Path(args.request)
    request = source.read_text(encoding="utf-8") if source.is_file() else args.request
    plan = run(request)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(plan, encoding="utf-8")
    print(plan)
