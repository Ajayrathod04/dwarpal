"""Optional Strands/Bedrock adapter; off by default."""
import os

def ask_agent(question: str):
    if os.getenv("ENABLE_STRANDS", "false").lower() != "true":
        return {"enabled":False,"answer":"Agent mode is off. The deterministic policy tools are available; enable Strands only after configuring and testing AWS model access."}
    try:
        from strands import Agent
        from strands.models import BedrockModel
        model = BedrockModel(model_id=os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"))
        agent = Agent(model=model, system_prompt="You are DWARPAL, a cautious action-governance assistant. Never claim an action executed unless tool evidence says so. Prefer policy evaluation and human escalation.")
        result = agent(question)
        return {"enabled":True,"answer":str(result)}
    except Exception as exc:
        return {"enabled":True,"error":f"Strands/Bedrock invocation failed ({type(exc).__name__}). Check dependencies, credentials, region and model access."}
