from agent import call_salesforce_agent
from sse_manager import event_manager

import json
from dotenv import load_dotenv
import os

load_dotenv()

class IntentDecoder:
    """
    Uses column data, metadata and user_input to decide which ontology is necessary 
    """
    def __init__(self, user_id):
        self.user_id = user_id
        self.ontology_library = self.get_ontology()
    
    def get_ontology(self):
        ontology = {}

        with open(file="ontology/Finance.json", mode="r") as finance:
            ontology["finance"] = finance.read()

        with open(file="ontology/Sales.json", mode="r") as sales:
            ontology["sales"] = sales.read()

        with open(file="ontology/HumanResources.json") as hr:
            ontology["human resources"] = hr.read()
        
        return ontology

    def decode_intent(self, metadata_profile):
        """
        Determines which Ontology to use based on the User's goal + Data look/feel.

        Input:\n
        user_prompt ( string ) - The input the user enters, describing what the data is for what to do with the data\n
        metadata_profile ( any[] ) - The column profiles of the data given by the user.\n

        Return:\n
        ontology ( string, any ){ } - A mapped ontology descibing common terms used by the firm.\n
        """
        # 1. Summarize the incoming data for the AI
        # We only need column names and inferred types from Layer 1
        data_summary = {
            col: info['inferred_type'] 
            for col, info in metadata_profile.items()
        }

        # 2. Construct the "System Prompt" for the LLM
        # This is where the "Innovation" happens: Prompt Engineering
        prompt = f"""
        - A User Request: Please map analyse this data. And Return ONLY one of these three text. Human Resources, Sales or Finance
        
        - Available Data Columns: {json.dumps(data_summary)}
        
        - All Available ontology Standards:{json.dumps(self.ontology_library, indent=2)}
        """
        
        # 3. Simulate the AI Response (In prod, this is openai.ChatCompletion.create)
        # For the demo/prototype, we can simulate logic or mock the call.
        print("--- Sending Prompt to LLM ---")
        print(prompt)
        print("-----------------------------")
        
        agent_id = os.getenv("DECODER_AGENT_ID") or ""

        # Either finance, sales or human resources
        response = call_salesforce_agent(message=prompt, agent_id=agent_id)

        if "Sales" in response:
            ontology_name = "sales"
        elif "Human Resources" in response:
            ontology_name = "Human Resources"
        else:
            ontology_name = "Finance"

        ontology = json.loads(self.ontology_library[ontology_name.lower()])

        fields = []
        for item in ontology["required_fields"]:
            fields.append({"Field": item[0], "Score": item[1]})

        event_data ={
            "id": 2,
            "title": "Decoded Intent",
            "text": "From the data provided, the inherited intent was semantically mapped to the corresponding ontology. Below is the mapped ontology as well as examples of fields in its data dictionary (note: the fields presented act as visaul examples, and are not directly related to fields in the provided dataset.)",
            "table": fields
        }
        
        return ontology, event_data