"""
Call a Salesforce Agentforce Agent using direct REST API calls
Based on Salesforce Agent API documentation
"""

import requests
import uuid
from typing import Dict, Any
import os
from dotenv import load_dotenv


load_dotenv()

def get_access_token(
    client_id: str,
    client_secret: str,
    my_domain_url: str
) -> str:
    """
    Get OAuth access token using client credentials flow
    
    Args:
        client_id: Connected App Consumer Key
        client_secret: Connected App Consumer Secret
        my_domain_url: Your My Domain URL (e.g., "mycompany.my.salesforce.com")
    
    Returns:
        Access token string
    """
    # Ensure my_domain_url doesn't have https://
    if my_domain_url.startswith("https://"):
        my_domain_url = my_domain_url.replace("https://", "")
    
    # IMPORTANT: Must use YOUR My Domain URL, not login.salesforce.com
    token_url = f"https://{my_domain_url}/services/oauth2/token"
    
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    response = requests.post(token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    # Better error handling
    if not response.ok:
        error_detail = response.json() if response.text else {}
        raise Exception(
            f"OAuth token request failed: {response.status_code}\n"
            f"Error: {error_detail.get('error', 'Unknown')}\n"
            f"Description: {error_detail.get('error_description', 'No description')}"
        )
    
    result = response.json()

    del result["access_token"]

    print(result)    
    return response.json()["access_token"]


def start_agent_session(
    agent_id: str,
    access_token: str,
    my_domain_url: str,
) -> Dict[str, Any]:
    """
    Start a new session with a Salesforce agent
    
    Args:
        agent_id: The 18-character agent ID (from URL in Setup)
        access_token: OAuth access token
        my_domain_url: Your Salesforce My Domain URL (e.g., "mycompany.my.salesforce.com")
        user_id: Optional 18-character Salesforce User ID. If not provided, uses the 
                Connected App's "Run As" user.
    
    Returns:
        Dictionary with session details including sessionId
    """
    url = f"https://api.salesforce.com/einstein/ai-agent/v1/agents/{agent_id}/sessions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Ensure my_domain_url is just the domain without https://
    if my_domain_url.startswith("https://"):
        my_domain_url = my_domain_url.replace("https://", "")
    
    payload = {
        "externalSessionKey": str(uuid.uuid4()),
        "instanceConfig": {
            "endpoint": f"https://{my_domain_url}"
        },
        "streamingCapabilities": {
            "chunkTypes": ["Text"]
        },
        "bypassUser": False
    }
    
    print("Sending Session Request...")
    response = requests.post(url, json=payload, headers=headers)
    
    # Better error handling with actual error message
    if not response.ok:
        error_detail = response.text if response.text else {}
        raise Exception(
            f"Failed to start agent session: {response.text}\n"
            f"URL: {url}\n"
            f"Error: \n"
            f"Message: \n"
            f"Full response: {error_detail}"
        )
    
    print("Agent Session Started")
    return response.json()


def send_message_to_agent(
    session_id: str,
    message: str,
    access_token: str,
    sequence_id: int = 1
) -> Dict[str, Any]:
    """
    Send a message to an agent session (synchronous)
    
    Args:
        session_id: Session ID from start_agent_session
        message: The message text to send
        access_token: OAuth access token
        sequence_id: Message sequence number (increment for each message in session)
    
    Returns:
        Agent's response
    """
    url = f"https://api.salesforce.com/einstein/ai-agent/v1/sessions/{session_id}/messages"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    payload = {
            "message": {
                "sequenceId": sequence_id,
                "type": "Text",
                "text": message
            }
        }
    print("Sending Message to Agent...")

    response = requests.post(url, json=payload, headers=headers)
  # Better error handling
    if not response.ok:
        error_detail = {}
        try:
            error_detail = response.json() if response.text else {}
        except:
            error_detail = {"raw_response": response.text}
        
        raise Exception(
            f"Failed to send message: {response.status_code}\n"
            f"Error: {error_detail.get('error', 'Unknown')}\n"
            f"Message: {error_detail.get('message', 'No message')}\n"
            f"Full response: {error_detail}"
        )
    
    return response.json()


def end_agent_session(
    session_id: str,
    access_token: str
) -> Dict[str, Any]:
    """
    End an agent session
    
    Args:
        session_id: Session ID to end
        access_token: OAuth access token
    
    Returns:
        Response from ending the session
    """
    url = f"https://api.salesforce.com/einstein/ai-agent/v1/sessions/{session_id}"
    
    headers = {
        'x-session-end-reason': 'UserRequest',
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    
    return response.json() if response.text else {"status": "ended"}


my_domain_url = os.getenv("SF_DOMAIN_URL") or "" # Your My Domain
client_id = os.getenv("SF_CLIENT_KEY") or ""  # Connected App Consumer Key
client_secret = os.getenv("SF_CLIENT_SECRET") or ""  # Connected App Consumer Secret

def call_salesforce_agent(
    agent_id: str,
    message: str,
) -> str:
    """
    High-level function to call a Salesforce agent with a single message
    
    Args:
        agent_id: The 18-character agent ID (from Setup > Agents > Agent URL)
        message: The message to send to the agent
        my_domain_url: Your My Domain URL (e.g., "mycompany.my.salesforce.com")
        client_id: Connected App Consumer Key
        client_secret: Connected App Consumer Secret
        user_id: Optional 18-character Salesforce User ID (if not provided, uses 
                Connected App's "Run As" user)
    
    Returns:
        Dictionary with:
            - response: Agent's text response
            - session_id: Session ID used
            - full_response: Complete API response
    
    Example:
        # Option 1: Use Connected App's "Run As" user (recommended)
        response = call_salesforce_agent(
            agent_id="0Xxbm000000owwrCAA",
            message="What can you help me with?",
            my_domain_url="mycompany.my.salesforce.com",
            client_id="3MVG9...",
            client_secret="1234..."
        )
        
        # Option 2: Specify a specific user
        response = call_salesforce_agent(
            agent_id="0Xxbm000000owwrCAA",
            message="What can you help me with?",
            my_domain_url="mycompany.my.salesforce.com",
            client_id="3MVG9...",
            client_secret="1234...",
            user_id="005xx000001X8Uz"  # 18-char User ID
        )
        
        print(response['response'])
    """


    # Get access token using YOUR My Domain URL
    access_token = get_access_token(client_id, client_secret, my_domain_url)
    
    # Start session
    session = start_agent_session(agent_id, access_token, my_domain_url)
    session_id = session["sessionId"]
    
    # Send message
    response = send_message_to_agent(session_id, message, access_token)
    
    # End session
    end_agent_session(session_id, access_token)
    
    return response["messages"][0]["message"]
