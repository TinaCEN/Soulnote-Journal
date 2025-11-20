# LM Studio Setup Guide

## Installation

1. **Download LM Studio**
   - Visit [lmstudio.ai](https://lmstudio.ai)
   - Download the version for your operating system
   - Install the application

## Recommended Models

For emotion analysis, we recommend using one of these models:

### Small Models (4-8GB RAM)
- **Llama 2 7B Chat** - Good balance of speed and accuracy
- **Mistral 7B Instruct** - Fast and efficient
- **Phi-2** - Lightweight but capable

### Medium Models (16GB+ RAM)
- **Llama 2 13B Chat** - Better understanding of nuanced emotions
- **Mixtral 8x7B** - Excellent performance

### Large Models (32GB+ RAM)
- **Llama 2 70B Chat** - Best accuracy for complex emotional analysis

## Setup Instructions

### 1. Download a Model

1. Open LM Studio
2. Click on the "Search" icon (🔍)
3. Search for "llama-2-7b-chat" or your preferred model
4. Click "Download"
5. Wait for the download to complete

### 2. Load the Model

1. Click on the "Chat" icon
2. Click "Select a model to load"
3. Choose your downloaded model
4. Wait for it to load into memory

### 3. Start the Local Server

1. Click on the "Local Server" tab (left sidebar)
2. Select your loaded model from the dropdown
3. Configure settings (optional):
   - **Port**: Default is 1234 (recommended)
   - **CORS**: Enable for web access
   - **Context Length**: 2048 or higher
   - **Temperature**: 0.7 (recommended for emotion analysis)
4. Click "Start Server"
5. You should see: "Server running on http://localhost:1234"

### 4. Verify Server

Test the server by visiting:
```
http://localhost:1234/v1/models
```

You should see a JSON response with your model information.

## Server Configuration

### Recommended Settings for Soulnote

```json
{
  "temperature": 0.7,
  "max_tokens": 500,
  "top_p": 0.9,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0
}
```

These are automatically set in the code, but you can adjust them in `models/lmstudio_client.py`.

## Troubleshooting

### Server Won't Start

- **Check Port**: Make sure port 1234 isn't already in use
- **Memory**: Ensure you have enough RAM for the model
- **Antivirus**: Add LM Studio to your antivirus exceptions

### Slow Responses

- Try a smaller model (7B instead of 13B)
- Reduce context length
- Close other applications to free up RAM
- Consider GPU acceleration if available

### Connection Errors

- Verify the server is running in LM Studio
- Check firewall settings
- Ensure you're using the correct port (default: 1234)
- Try restarting LM Studio

## API Endpoints

LM Studio provides OpenAI-compatible endpoints:

- `GET /v1/models` - List loaded models
- `POST /v1/chat/completions` - Chat completions (used by Soulnote)
- `POST /v1/completions` - Text completions

## Performance Tips

1. **GPU Acceleration**: If you have a compatible GPU, enable it in LM Studio settings
2. **Model Selection**: Start with smaller models and scale up if needed
3. **Context Length**: Use only what you need (2048 is usually sufficient)
4. **Batch Processing**: LM Studio can handle multiple requests efficiently

## Alternative Models

If LM Studio doesn't work for you, alternatives include:

- **Ollama** - Similar local LLM runner
- **text-generation-webui** - More advanced features
- **llama.cpp** - Command-line option

You would need to modify `models/lmstudio_client.py` to work with these alternatives.

## Resources

- [LM Studio Documentation](https://lmstudio.ai/docs)
- [Model Download Links](https://huggingface.co/models)
- [LM Studio Discord](https://discord.gg/lmstudio) - Community support

---

Once your server is running on http://localhost:1234, you're ready to use Soulnote!
