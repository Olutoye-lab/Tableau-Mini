import requests
import webbrowser
import json
import os
from urllib.parse import urlparse, parse_qs
from simple_salesforce.api import Salesforce
from typing import Optional, Dict


class SalesforceOAuthClient:
    """
    Salesforce OAuth client with automatic token refresh
    Stores tokens locally and reuses them across sessions
    """
    
    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        redirect_uri: str = 'http://localhost:8080/callback',
        domain: str = 'login',
        token_file: str = 'sf_tokens.json'
    ):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.redirect_uri = redirect_uri
        self.domain = domain
        self.token_file = token_file
        self.tokens: Dict = {}
        self.sf: Optional[Salesforce] = None
    
    def get_authorization_url(self) -> str:
        """Generate OAuth authorization URL"""
        return (
            f"https://{self.domain}.salesforce.com/services/oauth2/authorize?"
            f"response_type=code&"
            f"client_id={self.consumer_key}&"
            f"redirect_uri={self.redirect_uri}&"
            f"scope=api refresh_token offline_access"
        )
    
    def authorize(self) -> None:
        """
        Perform OAuth authorization flow
        Opens browser for user to login
        """
        print("=" * 70)
        print("SALESFORCE AUTHORIZATION")
        print("=" * 70)
        
        # Generate and open authorization URL
        auth_url = self.get_authorization_url()
        print("\nOpening browser for Salesforce login...")
        print(f"URL: {auth_url}\n")
        
        webbrowser.open(auth_url)
        
        # Wait for user to complete authorization
        print("After authorizing:")
        print("  1. Browser will redirect to: http://localhost:8080/callback?code=...")
        print("  2. You'll see an error page (this is normal)")
        print("  3. Copy the ENTIRE URL from the browser address bar\n")
        
        redirect_url = input("Paste the full redirect URL here: ").strip()
        
        # Extract authorization code
        try:
            parsed = urlparse(redirect_url)
            params = parse_qs(parsed.query)
            code = params['code'][0]
            print(f"\n✓ Authorization code received")
        except (KeyError, IndexError):
            raise Exception("Could not extract authorization code from URL")
        
        # Exchange code for tokens
        self._exchange_code_for_tokens(code)
    
    def _exchange_code_for_tokens(self, code: str) -> None:
        """Exchange authorization code for access and refresh tokens"""
        print("Exchanging authorization code for tokens...")
        
        token_url = f"https://{self.domain}.salesforce.com/services/oauth2/token"
        
        response = requests.post(token_url, data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.consumer_key,
            'client_secret': self.consumer_secret,
            'redirect_uri': self.redirect_uri
        })
        
        if not response.ok:
            raise Exception(f"Token exchange failed: {response.text}")
        
        self.tokens = response.json()
        self._save_tokens()
        print(f"✓ Tokens received and saved to {self.token_file}")
    
    def refresh_access_token(self) -> None:
        """Use refresh token to get new access token"""
        if not self.tokens or 'refresh_token' not in self.tokens:
            raise Exception("No refresh token available")
        
        print("⟳ Refreshing access token...")
        
        token_url = f"https://{self.domain}.salesforce.com/services/oauth2/token"
        
        response = requests.post(token_url, data={
            'grant_type': 'refresh_token',
            'refresh_token': self.tokens['refresh_token'],
            'client_id': self.consumer_key,
            'client_secret': self.consumer_secret
        })
        
        if not response.ok:
            raise Exception(f"Token refresh failed: {response.text}")
        
        new_tokens = response.json()
        
        # Preserve refresh token if not returned
        if 'refresh_token' not in new_tokens and 'refresh_token' in self.tokens:
            new_tokens['refresh_token'] = self.tokens['refresh_token']
        
        self.tokens = new_tokens
        self._save_tokens()
        print("✓ Access token refreshed")
    
    def _save_tokens(self) -> None:
        """Save tokens to file"""
        with open(self.token_file, 'w') as f:
            json.dump(self.tokens, f, indent=2)
    
    def _load_tokens(self) -> bool:
        """Load tokens from file"""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                self.tokens = json.load(f)
            return True
        return False
    
    def connect(self, force_reauth: bool = False) -> Salesforce:
        """
        Get authenticated Salesforce client
        Handles token refresh automatically
        
        Args:
            force_reauth: Force new authorization even if tokens exist
        """
        # Load existing tokens if available
        if not force_reauth and self._load_tokens():
            print(f"✓ Loaded tokens from {self.token_file}")
        else:
            # Need new authorization
            self.authorize()
        
        y = self.tokens
        # Try to connect with current token
        try:
            self.sf = Salesforce(
                instance_url=self.tokens['instance_url'],
                session_id=self.tokens['access_token']
            )
            
            # Test connection
            self.sf.query("SELECT Id FROM User LIMIT 1")
            print(f"✓ Connected to: {self.tokens['instance_url']}")
            return self.sf
            
        except Exception as e:
            # Token might be expired, try refresh
            if 'refresh_token' in self.tokens:
                self.refresh_access_token()
                
                self.sf = Salesforce(
                    instance_url=self.tokens['instance_url'],
                    session_id=self.tokens['access_token']
                )
                
                print(f"✓ Connected to: {self.tokens['instance_url']}")
                return self.sf
            else:
                raise Exception(f"Connection failed and no refresh token available: {e}")
    
    def disconnect(self) -> None:
        """Remove saved tokens"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
            print(f"✓ Removed {self.token_file}")
        self.tokens = {}
        self.sf = None


# Usage

consumer_key = os.getenv("SF_CLIENT_KEY") or ""
consumer_secret = os.getenv("SF_CLIENT_SECRET") or ""
redirect_url = os.getenv("SF_REDIRECT_URL") or ""

oauth_client = SalesforceOAuthClient(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    redirect_uri=redirect_url,
    domain='login'
)

# Get authenticated client (handles refresh automatically)
sf = oauth_client.connect()

# Use with your storage class
from salesforce_data_manager import SalesforceStorageManager
StorageManager = SalesforceStorageManager(sf)