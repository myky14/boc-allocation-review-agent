import sys
from boc_agent.skill.loader import SkillLoader
from boc_agent.runtime.agent import BOCReviewAgent

def main():
    print("==================================================")
    print("      Running Local Smoke Deployment Check        ")
    print("==================================================")

    # 1. Verify SKILL.md can load
    try:
        skill = SkillLoader().get_skill()
        print(f"[OK] Skill contract loaded successfully. Version: {skill.metadata.version}")
    except Exception as e:
        print(f"[ERROR] Failed to load skill contract: {e}")
        sys.exit(1)

    # 2. Verify BOCReviewAgent can run a query and returns a string
    try:
        agent = BOCReviewAgent()
        res = agent.run("What is Location 920?")
        if not isinstance(res, str):
            print(f"[ERROR] Agent.run did not return a string. Got type: {type(res)}")
            sys.exit(1)
        print("[OK] Agent run executed successfully and returned a string response.")
        
        # Verify last_trace exists
        if agent.last_trace is None:
            print("[ERROR] Agent.last_trace is None after run.")
            sys.exit(1)
        print(f"[OK] Agent trace captured successfully. ID: {agent.last_trace.trace_id}")
    except Exception as e:
        print(f"[ERROR] Failed to execute agent run: {e}")
        sys.exit(1)

    print("==================================================")
    print("    [SUCCESS] Smoke Deployment Checks Passed      ")
    print("==================================================")
    sys.exit(0)

if __name__ == "__main__":
    main()
