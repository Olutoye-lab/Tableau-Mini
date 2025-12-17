"""
Agentforce Agent API - Simple Agentic Call MVP
This script provides a straightforward implementation for making single calls to Salesforce Agentforce Agent API.
"""

import requests
import uuid
import os
from dotenv import load_dotenv
from typing import Dict, Optional
from dataclasses import dataclass

load_dotenv()

@dataclass
class AgentConfig:
    """Configuration for Agentforce Agent API"""
    domain_url: str
    consumer_key: str
    consumer_secret: str
    agent_id: str
    
    def __post_init__(self):
        """Validate required fields"""
        if not all([self.domain_url, self.consumer_key, self.consumer_secret, self.agent_id]):
            raise ValueError("All configuration fields are required")


class AgentforceClient:
    """Client for making single calls to Salesforce Agentforce Agent API"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.access_token: Optional[str] = None
        self.session_id: Optional[str] = None
        self.conversation_key: str = str(uuid.uuid4())
        self.base_url = f"https://{config.domain_url}"
        self.api_version = "v63.0"
        
    def authenticate(self) -> bool:
        """
        Authenticate with Salesforce and obtain access token
        Returns: True if authentication successful, False otherwise
        """
        token_url = f"{self.base_url}/services/oauth2/token"
        
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.config.consumer_key,
            'client_secret': self.config.consumer_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(token_url, data=payload, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            print(f"✓ Authenticated successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Authentication failed: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"  Response: { e.response.text}")
            return False
    
    def create_session(self, bypass_user: bool = True) -> Optional[str]:
        """
        Create a new agent session
        Args:
            bypass_user: If True, uses agent-assigned user; if False, uses token user
        Returns: Session ID if successful, None otherwise
        """
        if not self.access_token:
            print("✗ No access token. Please authenticate first.")
            return None
        
        session_url = (
            f"{self.base_url}/services/data/{self.api_version}/"
            f"messaging/agents/{self.config.agent_id}/sessions"
        )
        
        params = {'bypassUser': str(bypass_user).lower()}
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Conversation-Key': self.conversation_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(session_url, headers=headers, params=params, json={})
            response.raise_for_status()
            
            session_data = response.json()
            self.session_id = session_data.get('sessionId')
            
            print(f"✓ Session created: {self.session_id}")
            return self.session_id
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Session creation failed: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text}")
            return None
    
    def send_message(self, message: str) -> Optional[Dict]:
        """
        Send a message to the agent and get response
        Args:
            message: The message text to send
        Returns: Response data if successful, None otherwise
        """
        if not self.session_id:
            print("✗ No active session. Please create a session first.")
            return None
        else:
            print("SESSION ID", self.session_id)

        message_url = (
            f"{self.base_url}/services/data/{self.api_version}/"
            f"messaging/agents/{self.config.agent_id}/sessions/{self.session_id}/messages"
        )
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Conversation-Key': self.conversation_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'message': {
                'type': 'text',
                'text': message
            }
        }
        
        try:
            response = requests.post(message_url, headers=headers, json=payload)
            response.raise_for_status()
            
            response_data = response.json()
            print(f"✓ Message sent successfully")
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to send message: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text}")
            return None
    
    def end_session(self) -> bool:
        """
        End the current agent session
        Returns: True if successful, False otherwise
        """
        if not self.session_id:
            return True
        
        session_url = (
            f"{self.base_url}/services/data/{self.api_version}/"
            f"messaging/agents/{self.config.agent_id}/sessions/{self.session_id}"
        )
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Conversation-Key': self.conversation_key
        }
        
        try:
            response = requests.delete(session_url, headers=headers)
            response.raise_for_status()
            print(f"✓ Session ended")
            self.session_id = None
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to end session: {str(e)}")
            return False
    
    def execute_agent_call(self, message: str) -> Optional[str]:
        """
        Execute a complete agent call: create session, send message, get response, end session
        Args:
            message: The message to send to the agent
        Returns: Agent's response text if successful, None otherwise
        """
        try:
            # Create session
            if not self.create_session():
                return None
            
            # Send message
            response_data = self.send_message(message)
            if not response_data:
                return None
            
            # Extract response text
            agent_response = self._extract_response_text(response_data)
            
            # End session
            self.end_session()
            
            return agent_response
            
        except Exception as e:
            print(f"✗ Error during agent call: {str(e)}")
            self.end_session()
            return None
    
    def _extract_response_text(self, response_data: Dict) -> Optional[str]:
        """Extract text response from agent response data"""
        messages = response_data.get('messages', [])
        
        response_texts = []
        for msg in messages:
            if msg.get('type') == 'text':
                text = msg.get('text', '')
                if text:
                    response_texts.append(text)
        
        if response_texts:
            return '\n'.join(response_texts)
        
        return None


def load_config_from_env() -> AgentConfig:
    """Load configuration from environment variables"""
    return AgentConfig(
        domain_url=os.getenv('SF_DOMAIN_URL', ''),
        consumer_key=os.getenv('SF_CONSUMER_KEY', ''),
        consumer_secret=os.getenv('SF_CONSUMER_SECRET', ''),
        agent_id=os.getenv('SF_AGENT_ID', '')
    )


def main():
    """Main entry point for simple agentic call"""
    print("\n" + "="*60)
    print("Agentforce Agent API - Simple Agentic Call")
    print("="*60 + "\n")
    
    # Load configuration
    try:
        config = load_config_from_env()
    except ValueError as e:
        print(f"✗ Configuration error: {str(e)}")
        print("\nPlease set the following environment variables:")
        print("  - SF_DOMAIN_URL (e.g., 'mydomain.my.salesforce.com')")
        print("  - SF_CONSUMER_KEY")
        print("  - SF_CONSUMER_SECRET")
        print("  - SF_AGENT_ID")
        return
    
    # Initialize client
    client = AgentforceClient(config)
    
    # Authenticate
    print("Authenticating...")
    if not client.authenticate():
        print("\n✗ Authentication failed. Please check your credentials.")
        return
    
    # Get message from user or use default
    print("\nEnter your message for the agent:")
    user_message = input("> ").strip()
    
    if not user_message:
        user_message = "Hello, can you help me?"
        print(f"Using default message: {user_message}")
    
    # Execute agent call
    print(f"\nSending message to agent...")
    agent_response = client.execute_agent_call(user_message)
    
    # Display result
    if agent_response:
        print("\n" + "="*60)
        print("AGENT RESPONSE:")
        print("="*60)
        print(agent_response)
        print("="*60 + "\n")
    else:
        print("\n✗ Failed to get response from agent")
    
    print("Done!\n")


if __name__ == "__main__":
    main()