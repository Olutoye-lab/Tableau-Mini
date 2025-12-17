from agentforce_setup import call_agent

import json
from dotenv import load_dotenv
import os

load_dotenv()

class IntentDecoder:
    """
    Uses column data, metadata and user_input to decide which ontology is necessary 
    """
    def __init__(self):
        # In a real app, these load from a database
        self.ontology_library = self.get_ontology()
    
    def get_ontology(self):
        ontology = {}

        with open(file="ontology/Finance.json", mode="r") as finance:
            ontology["finance"] = finance

        with open(file="ontology/Sales.json", mode="r") as sales:
            ontology["sales"] = sales

        with open(file="ontology/HumanResources.json") as hr:
            ontology["human resources"] = hr

        return ontology

    def decode_intent(self, user_prompt, metadata_profile):
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
        system_prompt = f"""
        You are a Data Architect. 
        
        Goal: Match the user's intent and the available data columns to the correct Data Standard.

        You will be given:
        
        - A User Request: {user_prompt}
        
        - Available Data Columns: {json.dumps(data_summary)}
        
        - All Available ontology Standards:{json.dumps(self.ontology_library, indent=2)}
        
        Instructions:
        1. Analyze the User Request to understand the domain (Finance vs HR vs Sales).
        2. Look at the Data Columns to see which Standard fits best physically.
        3. Return ONLY the text of the best matching Standard.
        """
        
        # 3. Simulate the AI Response (In prod, this is openai.ChatCompletion.create)
        # For the demo/prototype, we can simulate logic or mock the call.
        print("--- Sending Prompt to LLM ---")
        print(system_prompt)
        print("-----------------------------")
        
        agent_name = os.getenv("ONTOLOGY_AGENT_NAME") or ""
        # Either finance, sales or human resources
        ontology_name = call_agent(system_prompt, agent_name)
        
        ontology = self.ontology_library[ontology_name.lower()]
        
        return ontology