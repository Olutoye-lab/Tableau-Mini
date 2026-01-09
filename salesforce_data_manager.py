
import subprocess
import json
from simple_salesforce.api import Salesforce
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dotenv import load_dotenv
import os
import requests

load_dotenv()

class SalesforceStorageManager:
    """
    Simple JSON storage using Salesforce.
    Automatically creates User_Reports__c object if it doesn't exist.
    """
    
    def __init__(self, sf: Salesforce, storage_object: str = 'User_Reports__c'):
        self.sf = sf
        self.storage_object = storage_object
        self._ensure_object_exists()
    
    def _ensure_object_exists(self):
        """Check if custom object exists, create if it doesn't"""
        try:
            # Test if object exists by querying it
            self.sf.query(f"SELECT Id FROM {self.storage_object} LIMIT 1")
            print(f"✓ {self.storage_object} exists")
        except Exception as e:
            if "INVALID_TYPE" in str(e) or "not supported" in str(e):
                print(f"⚠ {self.storage_object} doesn't exist")
                print(f"Creating {self.storage_object}...")
                self._create_custom_object()
            else:
                raise
    
    def _create_custom_object(self):
        """Create the User_Reports__c custom object via Metadata API"""
        print("\n" + "="*60)
        print("CREATING CUSTOM OBJECT")
        print("="*60)
        
        # Unfortunately, simple-salesforce doesn't support Metadata API for object creation
        # We need to use the Tooling API or Metadata API directly
        
        object_name = self.storage_object.replace('__c', '')
        
        # Create custom object using Tooling API
        url = f"{self.sf.base_url}tooling/sobjects/CustomObject"
        
        custom_object_payload = {
            "Label": object_name.replace('_', ' '),
            "PluralLabel": object_name.replace('_', ' ') + 's',
            "NameField": {
                "Type": "Text",
                "Label": "Report Name"
            },
            "DeploymentStatus": "Deployed",
            "SharingModel": "ReadWrite"
        }
        
        headers = {
            'Authorization': f'Bearer {self.sf.session_id}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=custom_object_payload)
            
            if response.status_code in [200, 201]:
                print(f"✓ Created custom object: {self.storage_object}")
                
                # Wait a moment for object to be available
                import time
                print("Waiting for object to be available...")
                time.sleep(3)
                
                # Create custom fields
                self._create_custom_fields()
            else:
                print(f"✗ Failed to create object: {response.status_code}")
                print(f"Response: {response.text}")
                raise Exception(f"Cannot create custom object. Please create it manually in Salesforce Setup.")
                
        except Exception as e:
            print(f"\n✗ Auto-creation failed: {e}")
            print("\n" + "="*60)
            print("MANUAL SETUP REQUIRED")
            print("="*60)
            print(f"\nPlease create the custom object manually:")
            print(f"1. Go to Setup → Object Manager → Create → Custom Object")
            print(f"2. Label: {object_name.replace('_', ' ')}")
            print(f"3. API Name: {object_name}")
            print(f"4. Add these fields:")
            print(f"   - User__c (Text, 255, External ID, Unique)")
            print(f"   - Report_List__c (Long Text Area, 131072)")
            print(f"   - Report_Data__c (Long Text Area, 131072)")
            print("="*60 + "\n")
            raise Exception("Custom object does not exist. Please create it manually (see instructions above).")
    
    def _create_custom_fields(self):
        """Create custom fields for the object"""
        print("\nCreating custom fields...")
        
        fields = [
            {
                "FullName": f"{self.storage_object}.User__c",
                "Label": "User",
                "Type": "Text",
                "Length": 255,
                "ExternalId": True,
                "Unique": True
            },
            {
                "FullName": f"{self.storage_object}.Report_List__c",
                "Label": "Report List",
                "Type": "LongTextArea",
                "Length": 131072,
                "VisibleLines": 5
            },
            {
                "FullName": f"{self.storage_object}.Report_Data__c",
                "Label": "Report Data",
                "Type": "LongTextArea",
                "Length": 131072,
                "VisibleLines": 5
            }
        ]
        
        url = f"{self.sf.base_url}tooling/sobjects/CustomField"
        headers = {
            'Authorization': f'Bearer {self.sf.session_id}',
            'Content-Type': 'application/json'
        }
        
        for field in fields:
            try:
                response = requests.post(url, headers=headers, json=field)
                if response.status_code in [200, 201]:
                    print(f"✓ Created field: {field['Label']}")
                else:
                    print(f"⚠ Field creation issue: {response.text}")
            except Exception as e:
                print(f"⚠ Error creating field {field['Label']}: {e}")
        
        print("\n✓ Custom object setup complete!")
        print("="*60 + "\n")
    
    @classmethod
    def connect(cls, username: str, password: str, security_token: str,
                domain: str = 'login', storage_object: str = 'User_Reports__c'):
        """Connect to Salesforce"""
        sf = Salesforce(
            username=username,
            password=password,
            security_token=security_token,
            domain=domain
        )
        return cls(sf, storage_object)
    
    @classmethod
    def connect_via_cli(cls, alias: str = 'myeventorg', storage_object: str = 'User_Reports__c'):
        """Connect via Salesforce CLI"""
        result = subprocess.run(
            ['sf', 'org', 'display', '--target-org', alias, '--json'],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.returncode != 0:
            raise Exception(f"CLI error: {result}\n\nRun: sf org login web --alias {alias}")
        
        org_info = json.loads(result.stdout)
        sf = Salesforce(
            instance_url=org_info['result']['instanceUrl'],
            session_id=org_info['result']['accessToken']
        )

        # sf = Salesforce(
        #     instance_url=os.getenv("InstanceUrl") or "",
        #     session_id=os.getenv("accessToken") or ""
        # )
        
        return cls(sf, storage_object)
    
    def _get_user_record(self, user_id: str) -> Optional[Dict]:
        """Get the storage record for a user"""
        query = f"SELECT Id, Report_List__c, Report_Data__c FROM {self.storage_object} WHERE User__c = '{user_id}' LIMIT 1"
        result = self.sf.query(query)
        
        if result['totalSize'] > 0:
            return result['records'][0]
        return None
    
    def add_report(self, user_id: str, report_data: Dict, 
                   report_name: str, metadata,
                   ) -> str:
        """
        Add a new report for a user
        
        Args:
            user_id: User identifier
            report_data: The actual JSON data to store
            report_name: Name of the report
            report_type: Type/category
            **metadata: Additional metadata fields
            
        Returns:
            report_id: Generated ID for the report
        """
        report_id = str(uuid.uuid4())
        record = self._get_user_record(user_id)
        
        if record:
            report_list = json.loads(record.get('Report_List__c') or '[]')
            all_report_data = json.loads(record.get('Report_Data__c') or '{}')
        else:
            report_list = []
            all_report_data = {}

        payload = {
            'report_id': report_id,
            'report_name': report_name,
            'created_at': datetime.now(timezone.utc).isoformat(),
        }
        
        payload.update(metadata)
        
        report_list.append(payload)
        
        all_report_data[report_id] = report_data
        
        update_data = {
            'Report_List__c': json.dumps(report_list),
            'Report_Data__c': json.dumps(all_report_data)
        }
        
        if record:
            getattr(self.sf, self.storage_object).update(record['Id'], update_data)
        else:
            update_data['User__c'] = user_id
            getattr(self.sf, self.storage_object).create(update_data)
        
        return report_id
    
    def get_report_list(self, user_id: str) -> List[Dict]:
        """Get list of report metadata for a user"""
        record = self._get_user_record(user_id)
        if not record:
            return []
        return json.loads(record.get('Report_List__c') or '[]')
    
    def get_report_data(self, user_id: str, report_id: str) -> Optional[Dict]:
        """Get specific report data"""
        record = self._get_user_record(user_id)
        if not record:
            return None
        report_data = json.loads(record.get('Report_Data__c') or '{}')
        return report_data.get(report_id)
    
    def get_all_reports(self, user_id: str) -> Dict:
        """Get both metadata list and all report data"""
        record = self._get_user_record(user_id)
        if not record:
            return {'metadata': [], 'data': {}}
        report_list = json.loads(record.get('Report_List__c') or '[]')
        report_data = json.loads(record.get('Report_Data__c') or '{}')
        return {'metadata': report_list, 'data': report_data}
    
    def update_report(self, user_id: str, report_id: str, 
                     report_data: Optional[Dict] = None,
                     **metadata_updates) -> bool:
        """Update report data and/or metadata"""
        record = self._get_user_record(user_id)
        if not record:
            return False
        
        report_list = json.loads(record.get('Report_List__c') or '[]')
        all_report_data = json.loads(record.get('Report_Data__c') or '{}')
        
        if metadata_updates:
            for i, meta in enumerate(report_list):
                if meta['report_id'] == report_id:
                    report_list[i].update(metadata_updates)
                    report_list[i]['updated_at'] = datetime.now(timezone.utc).isoformat()
                    break
            else:
                return False
        
        if report_data is not None:
            if report_id not in all_report_data:
                return False
            all_report_data[report_id] = report_data
        
        update_data = {
            'Report_List__c': json.dumps(report_list),
            'Report_Data__c': json.dumps(all_report_data)
        }
        getattr(self.sf, self.storage_object).update(record['Id'], update_data)
        return True
    
    def delete_report(self, user_id: str, report_id: str) -> bool:
        """Delete a report"""
        record = self._get_user_record(user_id)
        if not record:
            return False
        
        report_list = json.loads(record.get('Report_List__c') or '[]')
        all_report_data = json.loads(record.get('Report_Data__c') or '{}')
        
        report_list = [r for r in report_list if r['report_id'] != report_id]
        
        if report_id in all_report_data:
            del all_report_data[report_id]
        else:
            return False
        
        update_data = {
            'Report_List__c': json.dumps(report_list),
            'Report_Data__c': json.dumps(all_report_data)
        }
        getattr(self.sf, self.storage_object).update(record['Id'], update_data)
        return True
    
    def clear_user_reports(self, user_id: str) -> bool:
        """Delete all reports for a user"""
        record = self._get_user_record(user_id)
        if not record:
            return False
        
        update_data = {
            'Report_List__c': json.dumps([]),
            'Report_Data__c': json.dumps({})
        }
        getattr(self.sf, self.storage_object).update(record['Id'], update_data)
        return True
