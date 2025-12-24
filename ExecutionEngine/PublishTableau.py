import tableauserverclient as TSC
from dotenv import load_dotenv
from sse_manager import event_manager
import os
import json

load_dotenv()

class TableauCloudPublisher:
    def __init__(self, user_id, server_url, site_name, token, token_name):
        """
        Initialize connection details.
        Best Practice: Use Personal Access Tokens (PATs) for scripts, not passwords.
        """
        self.user_id = user_id
        self.server_url = server_url
        print(server_url, site_name, token, token_name)
        self.auth = TSC.PersonalAccessTokenAuth(
            site_id=site_name,
            token_name=token_name,
            personal_access_token=token,
        )
    
    # def get_token(self, client_id, secret_id, secret_val, user):
    #     token = jwt.encode(
    #         {
    #             "iss": client_id,
    #             "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10),
    #             "jti": str(uuid.uuid4()),
    #             "aud": "tableau",
    #             "sub": user,
    #             "scp": [
    #                 "tableau:content:read",
    #                 "tableau:content:write",
    #                 "tableau:datasources:create",    # For publishing datasources
    #                 "tableau:datasources:update",    # If updating existing
    #                 "tableau:projects:create",       # For creating projects
    #                 "tableau:projects:write"         # For modifying projects
    #             ]
    #         },
    #         secret_val,
    #         algorithm="HS256",
    #         headers={
    #             "kid": secret_id,
    #             "iss": client_id
    #         }
    #     )

    #     return token

    def publish(self, file_path, project_name="Default", datasource_name=None, certify=True):
        """
        Publishes the .hyper file and optionally marks it as 'Certified'.
        """

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Hyper file not found at: {file_path}")

        # Default datasource name to filename if not provided
        if not datasource_name:
            datasource_name = os.path.basename(file_path).replace(".hyper", "")

        print(f"Connecting to {self.server_url}...")
        
        server = TSC.Server(self.server_url, use_server_version=True)
        
        with server.auth.sign_in(self.auth):
            print("Authentication successful.")

            # 1. Find the Project ID (Target Folder)
            # We must scan projects to find the one matching 'project_name'
            all_projects, _ = server.projects.get()
            target_project = next((p for p in all_projects if p.name == project_name), None)
            
            if not target_project:
                print(f"Project '{project_name}' not found. Creating it...")
                new_project = TSC.ProjectItem(name=project_name)
                target_project = server.projects.create(new_project)
                print(f"Created new project with ID: {target_project.id}")

            print(f"Found Project '{project_name}' (ID: {target_project.id}). Publishing...")

            # 2. Define the Datasource configuration
            new_datasource = TSC.DatasourceItem(target_project.id, name=datasource_name)
            new_datasource.use_remote_query_agent = True # optimises for Hyper

            # 3. Upload the File (Overwrite if exists)
            published_ds = server.datasources.publish(
                new_datasource, 
                file_path, 
                mode=TSC.Server.PublishMode.Overwrite
            )
            
            print(f"✅ Published: '{published_ds.name}' (ID: {published_ds.id})")

            # 4. The 'Impact' Step: Certify the Data
            if certify:
                self._certify_datasource(server, published_ds)

    def _certify_datasource(self, server, datasource):
        """
        Internal helper to apply the 'Certified' badge.
        This updates the metadata on the server.
        """
        print("Applying 'Certified' badge...")
        
        # Modify the object properties
        datasource.certified = True
        datasource.certification_note = "Trusted by Smart Bridge Architecture. Verified clean."
        
        # Push the update
        server.datasources.update(datasource)
        print(f"🏆 Certification applied to '{datasource.name}'.")

