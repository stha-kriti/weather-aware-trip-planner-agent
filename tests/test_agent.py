import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import agent


def fake_client(*messages):
    replies = iter(messages)
    create = lambda **kw: SimpleNamespace(choices=[SimpleNamespace(message=next(replies))])
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


def tool_call(name="nope", arguments="{}"):
    return SimpleNamespace(content=None, tool_calls=[
        SimpleNamespace(id="1", function=SimpleNamespace(name=name, arguments=arguments))])


def test_returns_answer_when_no_tool_needed():
    client = fake_client(SimpleNamespace(content="Please tell me the city.", tool_calls=None))
    assert agent.run("plan a trip", client=client, model="m") == "Please tell me the city."


def test_tool_error_does_not_crash_the_loop():
    client = fake_client(tool_call("nope"), SimpleNamespace(content="DONE", tool_calls=None))
    assert agent.run("x", client=client, model="m") == "DONE"


def test_agent_stops_at_step_limit():
    """A model that always asks for a tool must still end with a final answer."""
    client = fake_client(tool_call(), tool_call(), SimpleNamespace(content="FINAL", tool_calls=None))
    assert agent.run("x", client=client, model="m", max_steps=2) == "FINAL"
