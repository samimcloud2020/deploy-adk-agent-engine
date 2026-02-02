import os
import sys
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from adk_short_bot.agent import root_agent

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

def list_deployments():
    return agent_engines.list()

def create_session(resource_id: str, user_id: str = "test_user") -> dict:
    return agent_engines.get(resource_id).create_session(user_id=user_id)

def list_sessions(resource_id: str, user_id: str = "test_user"):
    return agent_engines.get(resource_id).list_sessions(user_id=user_id)

def get_session(resource_id: str, user_id: str, session_id: str) -> dict:
    return agent_engines.get(resource_id).get_session(user_id=user_id, session_id=session_id)

def send_message(resource_id: str, user_id: str, session_id: str, message: str):
    remote_app = agent_engines.get(resource_id)
    return remote_app.stream_query(user_id=user_id, session_id=session_id, message=message)

def main():
    # Check environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")
    
    if not all([project_id, location, bucket]):
        sys.exit("Error: Missing required environment variables")
    
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location, staging_bucket=bucket)
    
    # 1. Create deployment
    print("Creating deployment...")
    resource_id = create()
    print(f"Resource ID: {resource_id}")
    
    # 2. List deployments
    print("\nListing all deployments:")
    deployments = list_deployments()
    for d in deployments:
        print(f"- {d.resource_name}")
    
    # 3. Create session
    print("\nCreating session...")
    user_id = "test_user"
    session = create_session(resource_id, user_id)
    session_id = session['id']
    print(f"Session created: {session_id}")
    
    # 4. List sessions for user
    print(f"\nListing sessions for user '{user_id}':")
    sessions = list_sessions(resource_id, user_id)
    for s in sessions:
        print(f"- {s['id']}")
    
    # 5. Get session details
    print(f"\nGetting session details for {session_id}:")
    session_details = get_session(resource_id, user_id, session_id)
    print(f"Session: {session_details['id']}")
    print(f"User: {session_details['user_id']}")
    print(f"Last update: {session_details['last_update_time']}")
    
    # 6. Send message
    print(f"\nSending message to session {session_id}:")
    message = "Shorten this message: Hello, how are you doing today?"
    print(f"Message: {message}")
    print("Response:")
    for event in send_message(resource_id, user_id, session_id, message):
        print(event, end="", flush=True)
    
    # 7. Delete deployment (optional - comment out to keep deployment)
    # print("\n\nDeleting deployment...")
    # delete(resource_id)
    # print("Deployment deleted")

if __name__ == "__main__":
    main()
