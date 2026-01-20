from huggingface_hub import snapshot_download

# Download the model to a local folder named 'my_model_files'
snapshot_download(
    repo_id="sentence-transformers/all-MiniLM-L6-v2", 
    local_dir="./my_model_files"
)