import os
import sys
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from adk_short_bot.agent import root_agent

# All required functions
def create() -> str:
    app = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)
    remote_app = agent_engines.create(
        agent_engine=app,
        requirements=["google-cloud-aiplatform[adk,agent_engines]"],
        extra_packages=["./adk_short_bot"],
    )
    return remote_app.resource_name

def delete(resource_id: str) -> None:
    agent_engines.get(resource_id).delete(force=True)

def list_deployments() -> list:
    return agent_engines.list()

def create_session(resource_id: str, user_id: str = "test_user") -> dict:
    return agent_engines.get(resource_id).create_session(user_id=user_id)

def list_sessions(resource_id: str, user_id: str = "test_user") -> list:
    return agent_engines.get(resource_id).list_sessions(user_id=user_id)

def get_session(resource_id: str, user_id: str, session_id: str) -> dict:
    return agent_engines.get(resource_id).get_session(user_id=user_id, session_id=session_id)

def send_message(resource_id: str, user_id: str, session_id: str, message: str):
    remote_app = agent_engines.get(resource_id)
    return remote_app.stream_query(user_id=user_id, session_id=session_id, message=message)

# Main execution
def main():
    # Check environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")
    
    if not all([project_id, location, bucket]):
        sys.exit("Error: Missing required environment variables")
    
    # Initialize
    vertexai.init(project=project_id, location=location, staging_bucket=bucket)
    
    # Run complete workflow
    print("Creating deployment...")
    resource_id = create()
    print(f"Created: {resource_id}")
    
    print("Creating session...")
    session = create_session(resource_id, "web_user")
    print(f"Session: {session['id']}")
    
    print("Sending message...")
    for event in send_message(resource_id, "web_user", session['id'], 
                            "Shorten this: Hello, how are you doing today?"):
        print(event, end="", flush=True)

if __name__ == "__main__":
    main()
