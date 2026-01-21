from sentence_transformers import SentenceTransformer
from sse_manager import event_manager
import pandas as pd
import faiss
import uuid


class SemanticMapper:
    def __init__(self,user_id, model_name="sentence-transformers/all-MiniLM-L6-v2", threshold=0.5):
        """
        Initializes the Mapper with a lightweight, high-speed embedding model.
        Args:
            model_name: The HuggingFace model to use.
            threshold: The confidence score (0.0 - 1.0) required to auto-map a field.
        """
        print(f"Loading Intelligence Core: {model_name}...")
        self.user_id = user_id
        self.model = SentenceTransformer(model_name)
        self.index = None  # The FAISS Vector Database
        self.ontology_fields = [] 
        self.threshold = threshold
        self.report_log = []
    
    def get_logs(self):
        return self.report_log
    
    def precompute_ontology(self, ontology_json):
        """
        Step 1: Precompute Ontology Embeddings.
        """
        self.ontology_fields = ontology_json['required_fields']
        print(f"Ingesting Ontology: {len(self.ontology_fields)} target fields found.")
        
        ontology_embeddings = self.model.encode([x[0] if type(x) != str else x for x in self.ontology_fields])
        faiss.normalize_L2(ontology_embeddings)
        
        dimension = ontology_embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(ontology_embeddings) # type: ignore
        print("Ontology vectorized and indexed successfully.")

    def map_columns(self, raw_input):
        """
        Maps columns to the precomputed ontology fields.
        Input: List, Pandas Series, or Pandas DataFrame.
        Returns:
        { column_name : {
            "mapped_to": ontology field,
            "confidence: float,
            "suggestion": other possible ontology fields,
            "status": "MAPPED or UNMAPPED"
            }
        }
        """
        # --- INPUT HANDLING LOGIC ---
        if isinstance(raw_input, pd.DataFrame):
            # If DataFrame, get column names
            raw_columns = raw_input.columns.tolist()
        elif isinstance(raw_input, pd.Series):
            # If Series, assume the values are the headers (common in metadata scanning)
            raw_columns = raw_input.tolist()
        elif isinstance(raw_input, list):
            raw_columns = raw_input
        else:
            raise ValueError("Input must be a Pandas DataFrame, Series, or List.")

        print(f"Processing {len(raw_columns)} raw columns...")
        
        # --- BATCH ENCODING ---
        raw_embeddings = self.model.encode(raw_columns)
        faiss.normalize_L2(raw_embeddings)
        
        # --- VECTOR SEARCH ---
        D, I = self.index.search(raw_embeddings, k=1) # type: ignore
        
        mapping_result = {}
        
        # --- THRESHOLDING ---
        for i, raw_col in enumerate(raw_columns):
            score = D[i][0]
            match_index = I[i][0]
            field = self.ontology_fields[match_index]
            matched_ontology_field = field[0] if type(field) != str else field
            
            # Structure the output for the next layer (Validation)
            if score >= self.threshold:
                mapping_result[raw_col] = {
                    "mapped_to": matched_ontology_field,
                    "confidence": float(f"{score:.4f}"),
                    "status": "AUTO_MAPPED"
                }
            else:
                mapping_result[raw_col] = {
                    "mapped_to": None,
                    "confidence": float(f"{score:.4f}"),
                    "suggestion": matched_ontology_field,
                    "status": "UNMAPPED"
                }

                self.report_log.append({
                    "id": str(uuid.uuid4()),
                    "column": raw_col,
                    "type": "Unmapped column",
                    "message": f"Unable to map the column header '{raw_col}' to any exact or similar descriptions in the enterprise data dictionary. Please check if the column exists in the data dictionary before proceeding.",
                    "status": "warning"
                })
                
        jsn = []
        for key, value in mapping_result.items():
            dct = {"column_name": key}
            dct.update(value)
            jsn.append(dct)

            if len(jsn) == 5:
                break

        event_data ={
            "id": 3,
            "title": "Semantic Mapping",
            "text": "Utilizing vector embeddings, fields have now been semantically mapped to their corresponding data ontology expressions.",
            "table": jsn
        }
                
        return mapping_result, event_data
    