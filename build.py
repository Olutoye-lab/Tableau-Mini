# build.py
from transformers import AutoTokenizer, AutoModel

def download():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"Downloading {model_name}...")
    # These commands pull the files into the local cache
    AutoTokenizer.from_pretrained(model_name)
    AutoModel.from_pretrained(model_name)
    print("Download complete!")

if __name__ == "__main__":
    download()