import os
import sys
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from adk_short_bot.agent import root_agent

def create() -> None:
    """Creates a new deployment."""
    # First wrap the agent in AdkApp
    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    # Now deploy to Agent Engine
    remote_app = agent_engines.create(
        agent_engine=app,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
        ],
        extra_packages=["./adk_short_bot"],
    )
    print(f"Created remote app: {remote_app.resource_name}")

def delete(resource_id: str) -> None:
    """Deletes an existing deployment."""
    remote_app = agent_engines.get(resource_id)
    remote_app.delete(force=True)
    print(f"Deleted remote app: {resource_id}")

def list_deployments() -> None:
    """Lists all deployments."""
    deployments = agent_engines.list()
    if not deployments:
        print("No deployments found.")
        return
    print("Deployments:")
    for deployment in deployments:
        print(f"- {deployment.resource_name}")

def create_session(resource_id: str, user_id: str) -> None:
    """Creates a new session for the specified user."""
    remote_app = agent_engines.get(resource_id)
    remote_session = remote_app.create_session(user_id=user_id)
    print("Created session:")
    print(f"  Session ID: {remote_session['id']}")
    print(f"  User ID: {remote_session['user_id']}")
    print(f"  App name: {remote_session['app_name']}")
    print(f"  Last update time: {remote_session['last_update_time']}")
    print("\nUse this session ID when sending messages.")

def list_sessions(resource_id: str, user_id: str) -> None:
    """Lists all sessions for the specified user."""
    remote_app = agent_engines.get(resource_id)
    sessions = remote_app.list_sessions(user_id=user_id)
    print(f"Sessions for user '{user_id}':")
    for session in sessions:
        print(f"- Session ID: {session['id']}")

def get_session(resource_id: str, user_id: str, session_id: str) -> None:
    """Gets a specific session."""
    remote_app = agent_engines.get(resource_id)
    session = remote_app.get_session(user_id=user_id, session_id=session_id)
    print("Session details:")
    print(f"  ID: {session['id']}")
    print(f"  User ID: {session['user_id']}")
    print(f"  App name: {session['app_name']}")
    print(f"  Last update time: {session['last_update_time']}")

def send_message(resource_id: str, user_id: str, session_id: str, message: str) -> None:
    """Sends a message to the deployed agent."""
    remote_app = agent_engines.get(resource_id)

    print(f"Sending message to session {session_id}:")
    print(f"Message: {message}")
    print("\nResponse:")
    for event in remote_app.stream_query(
        user_id=user_id,
        session_id=session_id,
        message=message,
    ):
        print(event)

def main():
    """Main function that runs the complete ADK workflow."""
    # Check environment variables
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")
    
    if not all([project_id, location, bucket]):
        print("Error: Missing required environment variables")
        sys.exit(1)
    
    # Initialize Vertex AI
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=bucket,
    )
    
    # Run complete workflow
    print("=" * 60)
    print("Starting ADK Agent Workflow")
    print("=" * 60)
    
    # 1. Create deployment
    print("\n1. Creating deployment...")
    create()
    
    # Note: In actual execution, we need to store the resource_id
    # For demonstration, we'll list deployments to see what was created
    print("\n2. Listing deployments...")
    list_deployments()
    
    print("\nNote: To continue with the workflow, you need to:")
    print("1. Get the resource_id from the deployment list above")
    print("2. Update the code with the actual resource_id")
    print("3. Uncomment and run the following steps:")
    print("\n# resource_id = 'your_resource_id_here'")
    print("# user_id = 'test_user'")
    print("# create_session(resource_id, user_id)")
    print("# list_sessions(resource_id, user_id)")
    print("# get_session(resource_id, user_id, 'session_id_here')")
    print("# send_message(resource_id, user_id, 'session_id_here', 'Your message')")
    print("# delete(resource_id)")

if __name__ == "__main__":
    main()
