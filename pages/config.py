MODEL_SETTINGS = {
    "temperature": 0.3,
    "max_tokens": 1024,
}

AVAILABLE_MODELS = {
    "deepseek_qwen": "deepseek-r1-distill-qwen-32b",
    "llama_model": "deepseek-r1-distill-llama-70b",
}

AVAILABLE_AGENTS = {
    "Helpful Assistant": {"model": "llama_model", "system_prompt": "", "settings": MODEL_SETTINGS},
    "Code Expert": {"model": "llama_model", "system_prompt": "", "settings": MODEL_SETTINGS},
    "Document Analyzer": {"model": "llama_model", "system_prompt": "", "settings": MODEL_SETTINGS},
}
