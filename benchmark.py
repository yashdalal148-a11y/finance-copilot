import time
from app.core.config import load_config
from app.core.llm_client import GeminiClient
from app.core.speech_client import SpeechClient
from app.core.session import SessionMemory
from app.agents.context_agent import ContextAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.finance_expert_agent import FinanceExpertAgent
from app.agents.follow_up_agent import FollowUpAgent
from app.agents.interview_agent import InterviewAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.listener_agent import ListenerAgent
from app.agents.orchestrator import Orchestrator

def run_benchmark():
    cfg = load_config()
    llm = GeminiClient(api_key=cfg.gemini_api_key, model_name=cfg.gemini_model)
    speech = SpeechClient(model_size=cfg.whisper_model_size, device=cfg.whisper_device, compute_type=cfg.whisper_compute_type)
    memory = SessionMemory()
    
    listener = ListenerAgent(speech_client=speech)
    context = ContextAgent(memory=memory)
    interview = InterviewAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    knowledge_ag = KnowledgeAgent(knowledge_dir=cfg.knowledge_dir, max_passages=cfg.max_knowledge_passages)
    expert = FinanceExpertAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    follow_up = FollowUpAgent(llm=llm, prompts_dir=cfg.prompts_dir)
    evaluation = EvaluationAgent(llm=llm, prompts_dir=cfg.prompts_dir)

    orchestrator = Orchestrator(
        listener=listener, context=context, interview=interview,
        knowledge=knowledge_ag, expert=expert, follow_up=follow_up,
        evaluation=evaluation, memory=memory
    )

    question = "Walk me through a DCF analysis."
    
    print(f"Benchmarking V1.1 Pipeline (Question: '{question}')...")
    
    t0 = time.perf_counter()
    result = orchestrator.run_text(question)
    t1 = time.perf_counter()
    
    print(f"Total Latency: {(t1 - t0)*1000:.0f} ms")
    for t in result.timings:
        print(f" - {t.agent_name}: {t.duration_ms:.0f} ms")

if __name__ == "__main__":
    run_benchmark()
