import os
import glob

replacements = {
    "story_agent.py": ("TaskType.STORY_INTELLIGENCE", "generate_json("),
    "resume_agent.py": ("TaskType.RESUME_PARSING", "generate_json("),
    "red_flag_agent.py": ("TaskType.RED_FLAG", "generate_json("),
    "offer_agent.py": ("TaskType.OFFER_PROBABILITY", "generate_json("),
    "jd_agent.py": ("TaskType.JD_PARSING", "generate_json("),
    "interview_agent.py": ("TaskType.CLASSIFICATION", "generate_json("),
    "intent_agent.py": ("TaskType.INTENT_ANALYSIS", "generate_json("),
    "gap_agent.py": ("TaskType.GAP_ANALYSIS", "generate_json("),
    "follow_up_agent.py": ("TaskType.FOLLOW_UP", "generate_json("),
    "fit_agent.py": ("TaskType.FIT_ANALYSIS", "generate_json("),
    "finance_expert_agent.py": ("TaskType.EXPERT_ANSWER", "generate("),
    "evaluation_agent.py": ("TaskType.EVALUATION", "generate_json("),
    "battlefield_agent.py": ("TaskType.BATTLEFIELD_MAP", "generate_json(")
}

for file_path in glob.glob("app/agents/*.py"):
    filename = os.path.basename(file_path)
    if filename not in replacements:
        continue
        
    task_enum, gen_call = replacements[filename]
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Replace import
    content = content.replace("from app.core.llm_client import GeminiClient", "from app.core.llm_router import LLMRouter\nfrom app.core.models import TaskType")
    
    # Replace signature
    content = content.replace("llm: GeminiClient", "llm: LLMRouter")
    
    # Add task_type to generate calls
    # E.g. self._llm.generate_json(prompt, temperature=0.7) -> self._llm.generate_json(prompt, temperature=0.7, task_type=TaskType.STORY_INTELLIGENCE)
    # E.g. self._llm.generate(prompt) -> self._llm.generate(prompt, task_type=TaskType.EXPERT_ANSWER)
    
    # Simple replace
    # We will just replace `self._llm.generate_json(` with `self._llm.generate_json(task_type=TaskType.XXX, `
    # Or `self._llm.generate(` with `self._llm.generate(task_type=TaskType.XXX, `
    
    if "generate_json(" in content:
        content = content.replace("self._llm.generate_json(", f"self._llm.generate_json(task_type={task_enum}, ")
    elif "self._llm.generate(" in content:
        content = content.replace("self._llm.generate(", f"self._llm.generate(task_type={task_enum}, ")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
print("Updated all agents successfully.")
