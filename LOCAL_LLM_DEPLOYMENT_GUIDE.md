# Local LLM Deployment Guide: Llama 3.1 8B Instant on AWS EC2

## Overview

This guide provides step-by-step instructions to replace the Groq AI API with a self-hosted Llama 3.1 8B Instant model deployed on AWS EC2. The deployment will maintain API compatibility with the existing codebase, allowing for seamless integration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS EC2 Setup](#aws-ec2-setup)
3. [Installing Llama 3.1 8B Model](#installing-llama-31-8b-model)
4. [Setting Up Inference Server](#setting-up-inference-server)
5. [Creating OpenAI-Compatible API](#creating-openai-compatible-api)
6. [Code Modifications](#code-modifications)
7. [Fine-Tuning for Food Ordering](#fine-tuning-for-food-ordering)
8. [Testing and Validation](#testing-and-validation)
9. [Security Considerations](#security-considerations)
10. [Cost Analysis](#cost-analysis)
11. [Performance Optimization](#performance-optimization)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Knowledge
- Basic understanding of AWS EC2
- Python programming
- Linux command line
- API design concepts
- Machine learning basics

### Required Accounts & Tools
- AWS account with EC2 access
- Hugging Face account (for model access)
- SSH client
- Git

---

## AWS EC2 Setup

### Step 1: Choose the Right EC2 Instance

For Llama 3.1 8B model, you need an instance with GPU support:

**Recommended Instances:**
- **g5.xlarge** (1x NVIDIA A10G, 24GB GPU RAM) - **Recommended for production**
  - Cost: ~$1.00/hour on-demand
  - Sufficient for inference with good performance
  
- **g4dn.xlarge** (1x NVIDIA T4, 16GB GPU RAM) - Budget option
  - Cost: ~$0.50/hour on-demand
  - Works but slower inference

- **g5.2xlarge** (1x NVIDIA A10G, 24GB GPU RAM) - Better performance
  - Cost: ~$1.21/hour on-demand
  - Better for fine-tuning

### Step 2: Launch EC2 Instance

```bash
# Using AWS CLI (or use AWS Console)
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \  # Ubuntu 22.04 Deep Learning AMI
    --instance-type g5.xlarge \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxx \
    --subnet-id subnet-xxxxxxxx \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":200,"VolumeType":"gp3"}}]' \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=LLM-Server}]'
```

**Storage Recommendations:**
- Minimum: 150 GB (model ~16GB + dependencies + fine-tuning data)
- Recommended: 200 GB for fine-tuning workspace

### Step 3: Configure Security Group

Create/update security group rules:

```bash
# Allow SSH
Port: 22, Protocol: TCP, Source: Your IP

# Allow HTTP (for API)
Port: 8000, Protocol: TCP, Source: Your Django App IP

# Allow HTTPS (optional, for secure API)
Port: 443, Protocol: TCP, Source: Your Django App IP
```

### Step 4: Connect to Instance

```bash
ssh -i your-key.pem ubuntu@<EC2-PUBLIC-IP>
```

### Step 5: Update System

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git htop nvtop
```

### Step 6: Verify GPU

```bash
nvidia-smi  # Should show NVIDIA A10G or T4
```

---

## Installing Llama 3.1 8B Model

### Step 1: Install Dependencies

```bash
# Create virtual environment
python3 -m venv ~/llm-env
source ~/llm-env/bin/activate

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install Hugging Face libraries
pip install transformers accelerate bitsandbytes sentencepiece protobuf
```

### Step 2: Get Model Access

Llama models require approval from Meta:

1. Visit: https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
2. Request access (usually approved within hours)
3. Generate HF token: https://huggingface.co/settings/tokens

### Step 3: Download Model

```bash
# Login to Hugging Face
pip install huggingface_hub
huggingface-cli login  # Enter your token

# Download model (takes 15-30 minutes)
python3 << EOF
from huggingface_hub import snapshot_download

model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
snapshot_download(
    repo_id=model_id,
    local_dir="/home/ubuntu/models/llama-3.1-8b-instruct",
    local_dir_use_symlinks=False
)
EOF
```

Model will be stored at: `/home/ubuntu/models/llama-3.1-8b-instruct`

---

## Setting Up Inference Server

We'll use **vLLM** - the fastest inference server with OpenAI-compatible API.

### Step 1: Install vLLM

```bash
pip install vllm
```

### Step 2: Create Server Script

Create `/home/ubuntu/start_llm_server.sh`:

```bash
#!/bin/bash
source ~/llm-env/bin/activate

vllm serve meta-llama/Meta-Llama-3.1-8B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --model /home/ubuntu/models/llama-3.1-8b-instruct \
    --tensor-parallel-size 1 \
    --max-model-len 2048 \
    --gpu-memory-utilization 0.9 \
    --dtype auto \
    --api-key "your-secure-api-key-here"
```

Make it executable:

```bash
chmod +x /home/ubuntu/start_llm_server.sh
```

### Step 3: Create Systemd Service (Auto-restart)

Create `/etc/systemd/system/llm-server.service`:

```ini
[Unit]
Description=vLLM LLM Inference Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/home/ubuntu/start_llm_server.sh
Restart=always
RestartSec=10
Environment="PATH=/home/ubuntu/llm-env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable llm-server
sudo systemctl start llm-server

# Check status
sudo systemctl status llm-server

# View logs
sudo journalctl -u llm-server -f
```

### Step 4: Test Server

```bash
curl http://localhost:8000/v1/models
```

Expected output:
```json
{
  "object": "list",
  "data": [
    {
      "id": "meta-llama/Meta-Llama-3.1-8B-Instruct",
      "object": "model",
      "created": 1234567890,
      "owned_by": "meta-llama"
    }
  ]
}
```

---

## Creating OpenAI-Compatible API

vLLM automatically provides OpenAI-compatible endpoints:

### Available Endpoints

- `POST /v1/chat/completions` - Chat completion (like Groq)
- `GET /v1/models` - List models
- `POST /v1/completions` - Text completion

### Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "messages": [
      {"role": "system", "content": "You are a helpful restaurant assistant."},
      {"role": "user", "content": "I would like to order a pizza"}
    ],
    "max_tokens": 100,
    "temperature": 0.3
  }'
```

---

## Code Modifications

### Step 1: Create New LLM Client

Edit `/tmp/workspace/talharamzandigital/AI_Waiter_Order/django_ai_waiter/llm_client.py`:

```python
import openai
from typing import List, Dict
from django.conf import settings

class LocalLLMClient(BaseLLMClient):
    """Client for local vLLM server with OpenAI-compatible API"""
    
    def __init__(self):
        self.api_key = settings.AI_WAITER.get("LOCAL_LLM_API_KEY", "")
        self.base_url = settings.AI_WAITER.get("LOCAL_LLM_BASE_URL", "")
        self.model = settings.AI_WAITER.get("LOCAL_LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")
        
        # Initialize OpenAI client pointing to local vLLM
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, str]:
        """
        Send chat request to local LLM server
        
        Args:
            system_prompt: System instruction
            messages: Conversation history
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
        
        Returns:
            Dict with response content
        """
        # Prepare messages with system prompt
        formatted_messages = [{"role": "system", "content": system_prompt}]
        formatted_messages.extend(messages)
        
        # Get parameters
        max_tokens = kwargs.get("max_tokens", settings.AI_WAITER.get("AI_MAX_TOKENS", 1024))
        temperature = kwargs.get("temperature", settings.AI_WAITER.get("AI_TEMPERATURE", 0.3))
        
        try:
            # Call local vLLM server
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            # Extract response
            content = response.choices[0].message.content
            
            return {
                "role": "assistant",
                "content": content,
                "model": self.model,
                "mock": False
            }
            
        except Exception as e:
            # Log error and raise
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Local LLM API error: {str(e)}")
            raise
```

### Step 2: Update Factory Function

In the same file, modify `get_llm_client()`:

```python
def get_llm_client(use_real: bool = True) -> BaseLLMClient:
    """Factory function to get LLM client"""
    
    if not use_real:
        return MockLLMClient()
    
    # Check which client to use
    use_local = settings.AI_WAITER.get("USE_LOCAL_LLM", False)
    
    if use_local:
        # Use local LLM server
        api_key = settings.AI_WAITER.get("LOCAL_LLM_API_KEY", "")
        if not api_key:
            logger.warning("Local LLM API key not configured, falling back to mock")
            return MockLLMClient()
        return LocalLLMClient()
    else:
        # Use Groq (existing code)
        api_key = settings.AI_WAITER.get("GROQ_API_KEY", "")
        if not api_key:
            logger.warning("Groq API key not configured, falling back to mock")
            return MockLLMClient()
        return GroqLLMClient()
```

### Step 3: Update Django Settings

Edit `/tmp/workspace/talharamzandigital/AI_Waiter_Order/django_ai_waiter/app_settings.py`:

```python
AI_WAITER = {
    # Existing Groq settings
    "GROQ_API_KEY": os.environ.get("GROQ_API_KEY", ""),
    "AI_MODEL": os.environ.get("AI_MODEL", "llama-3.1-8b-instant"),
    
    # New local LLM settings
    "USE_LOCAL_LLM": os.environ.get("USE_LOCAL_LLM", "false").lower() == "true",
    "LOCAL_LLM_BASE_URL": os.environ.get("LOCAL_LLM_BASE_URL", "http://your-ec2-ip:8000/v1"),
    "LOCAL_LLM_API_KEY": os.environ.get("LOCAL_LLM_API_KEY", ""),
    "LOCAL_LLM_MODEL": os.environ.get("LOCAL_LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct"),
    
    # Common settings
    "AI_MAX_TOKENS": int(os.environ.get("AI_MAX_TOKENS", "1024")),
    "AI_TEMPERATURE": float(os.environ.get("AI_TEMPERATURE", "0.3")),
}
```

### Step 4: Update Environment Variables

Add to `.env` file:

```bash
# Toggle between Groq and Local LLM
USE_LOCAL_LLM=true

# Local LLM Configuration
LOCAL_LLM_BASE_URL=http://<EC2-PUBLIC-IP>:8000/v1
LOCAL_LLM_API_KEY=your-secure-api-key-here
LOCAL_LLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct

# Keep Groq as fallback
GROQ_API_KEY=your-groq-key
```

### Step 5: Update Requirements

Add to `requirements.txt`:

```
openai>=1.0.0
```

Install:

```bash
pip install openai
```

---

## Fine-Tuning for Food Ordering

### Step 1: Prepare Training Data

Create training dataset in JSONL format (`training_data.jsonl`):

```json
{"messages": [{"role": "system", "content": "You are a restaurant ordering assistant."}, {"role": "user", "content": "I'd like to order a pizza"}, {"role": "assistant", "content": "Great! What size pizza would you like? We have small, medium, and large."}]}
{"messages": [{"role": "system", "content": "You are a restaurant ordering assistant."}, {"role": "user", "content": "Large pepperoni pizza"}, {"role": "assistant", "content": "Excellent choice! One large pepperoni pizza. Would you like any drinks or sides with that?"}]}
{"messages": [{"role": "system", "content": "You are a restaurant ordering assistant."}, {"role": "user", "content": "Add a Coke"}, {"role": "assistant", "content": "Added a Coke to your order. Your current order: 1 large pepperoni pizza and 1 Coke. Anything else?"}]}
{"messages": [{"role": "system", "content": "You are a restaurant ordering assistant."}, {"role": "user", "content": "That's all"}, {"role": "assistant", "content": "Perfect! Let me confirm your order: 1 large pepperoni pizza and 1 Coke. Would you like to proceed with this order?"}]}
```

**Best Practices:**
- Collect real order conversations
- Include edge cases (modifications, allergies, etc.)
- 100-1000 examples recommended
- Validate data quality

### Step 2: Install Fine-Tuning Libraries

On EC2:

```bash
pip install peft trl datasets
```

### Step 3: Create Fine-Tuning Script

Create `/home/ubuntu/fine_tune.py`:

```python
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset

# Load model and tokenizer
model_name = "/home/ubuntu/models/llama-3.1-8b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
    load_in_8bit=True  # Use 8-bit for lower memory
)

# Prepare for LoRA training
model = prepare_model_for_kbit_training(model)

# LoRA configuration
lora_config = LoraConfig(
    r=16,  # Rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# Load dataset
dataset = load_dataset("json", data_files="training_data.jsonl")

# Tokenize function
def tokenize_function(examples):
    return tokenizer(examples["messages"], truncation=True, max_length=512)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="/home/ubuntu/fine_tuned_model",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,
    save_strategy="epoch",
    logging_steps=10,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
)

# Train
trainer.train()

# Save fine-tuned model
model.save_pretrained("/home/ubuntu/fine_tuned_model")
tokenizer.save_pretrained("/home/ubuntu/fine_tuned_model")
```

### Step 4: Run Fine-Tuning

```bash
python3 fine_tune.py
```

**Expected Time:** 1-4 hours depending on dataset size

### Step 5: Deploy Fine-Tuned Model

Update `/home/ubuntu/start_llm_server.sh`:

```bash
vllm serve meta-llama/Meta-Llama-3.1-8B-Instruct \
    --model /home/ubuntu/fine_tuned_model \  # Changed path
    # ... rest of parameters
```

Restart service:

```bash
sudo systemctl restart llm-server
```

---

## Testing and Validation

### Step 1: Unit Test

Create test script:

```python
# test_local_llm.py
import os
os.environ["USE_LOCAL_LLM"] = "true"

from django_ai_waiter.llm_client import get_llm_client

client = get_llm_client(use_real=True)

response = client.chat(
    system_prompt="You are a restaurant ordering assistant.",
    messages=[
        {"role": "user", "content": "I'd like to order a pizza"}
    ]
)

print("Response:", response["content"])
assert response["mock"] == False
assert len(response["content"]) > 0
print("✓ Test passed!")
```

### Step 2: Integration Test

Test via Django API:

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "I want to order a pizza"
  }'
```

### Step 3: Load Testing

Use Apache Bench:

```bash
ab -n 100 -c 10 -p payload.json -T application/json \
  http://localhost:8000/api/chat/
```

**Performance Targets:**
- Response time: < 2 seconds
- Throughput: > 10 requests/second
- Error rate: < 1%

### Step 4: Compare with Groq

Run same tests with both backends:

```bash
# Groq
USE_LOCAL_LLM=false python test_local_llm.py

# Local
USE_LOCAL_LLM=true python test_local_llm.py
```

Compare:
- Response quality
- Response time
- Cost per request

---

## Security Considerations

### 1. Network Security

```bash
# Restrict API access to your Django server IP only
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxx \
    --protocol tcp \
    --port 8000 \
    --source-group sg-yyyyyyyy  # Django server security group
```

### 2. API Authentication

- Use strong API keys (generate with `openssl rand -hex 32`)
- Rotate keys monthly
- Store in AWS Secrets Manager

### 3. HTTPS/TLS

Install Nginx as reverse proxy:

```bash
sudo apt install nginx certbot python3-certbot-nginx

# Configure Nginx
sudo nano /etc/nginx/sites-available/llm-api
```

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Rate Limiting

In vLLM server, add rate limiting:

```python
# Use nginx rate limiting or implement in Django middleware
```

### 5. Monitoring

Install CloudWatch agent:

```bash
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

Monitor:
- CPU/GPU usage
- Memory usage
- Request latency
- Error rates

---

## Cost Analysis

### Monthly Cost Breakdown (g5.xlarge)

**AWS EC2:**
- Instance: $730/month (24/7 on-demand)
- Storage (200GB): $20/month
- Data transfer: $5-50/month (varies)
- **Total:** ~$755-805/month

**Cost Reduction Strategies:**

1. **Reserved Instances (1-year):**
   - Save ~40%: $440/month

2. **Spot Instances:**
   - Save ~70%: $220/month
   - Risk: Can be interrupted

3. **Auto-scaling:**
   - Run only during business hours (12h/day)
   - Cost: $365/month

### Groq vs Local Cost Comparison

**Groq API:**
- Cost: $0.10 per million tokens
- 10K requests/day × 500 tokens avg = 150M tokens/month
- **Monthly cost:** $15

**Local LLM:**
- Fixed cost: $220-805/month
- Unlimited requests
- **Break-even:** ~2M requests/month

**Recommendation:**
- Start with Groq for < 100K requests/month
- Switch to local for > 100K requests/month
- Consider hybrid: Groq for peaks, local for base load

---

## Performance Optimization

### 1. Batch Processing

```python
# In vLLM server config
--max-num-batched-tokens 8192
--max-num-seqs 256
```

### 2. Quantization

Use 4-bit quantization for 2x speedup:

```bash
vllm serve meta-llama/Meta-Llama-3.1-8B-Instruct \
    --quantization awq \  # or gptq
    # ...
```

### 3. Tensor Parallelism

For multi-GPU instances (g5.2xlarge with 2 GPUs):

```bash
--tensor-parallel-size 2
```

### 4. Caching

Implement Redis caching in Django:

```python
from django.core.cache import cache

def get_llm_response(prompt):
    cache_key = f"llm:{hash(prompt)}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    response = llm.chat(...)
    cache.set(cache_key, response, timeout=3600)  # 1 hour
    return response
```

### 5. Connection Pooling

Use persistent connections:

```python
# In LocalLLMClient.__init__
self.client = openai.OpenAI(
    api_key=self.api_key,
    base_url=self.base_url,
    max_retries=3,
    timeout=30.0
)
```

---

## Troubleshooting

### Issue 1: Out of Memory (OOM)

**Symptoms:** Server crashes, CUDA OOM errors

**Solutions:**
```bash
# Reduce max model length
--max-model-len 1024

# Reduce GPU memory usage
--gpu-memory-utilization 0.8

# Enable CPU offloading
--cpu-offload-gb 4
```

### Issue 2: Slow Response Time

**Symptoms:** > 5 second latency

**Solutions:**
- Check GPU usage: `nvidia-smi`
- Reduce max_tokens in requests
- Enable quantization
- Use faster instance type

### Issue 3: Model Not Loading

**Symptoms:** Server fails to start

**Solutions:**
```bash
# Check model path
ls -la /home/ubuntu/models/llama-3.1-8b-instruct

# Verify Hugging Face token
huggingface-cli whoami

# Check logs
sudo journalctl -u llm-server -n 100
```

### Issue 4: Connection Refused

**Symptoms:** Django can't connect to LLM server

**Solutions:**
```bash
# Check if server is running
sudo systemctl status llm-server

# Test locally
curl http://localhost:8000/v1/models

# Check firewall
sudo ufw status

# Verify security group rules
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx
```

### Issue 5: API Key Authentication Failed

**Symptoms:** 401 Unauthorized errors

**Solutions:**
- Verify API key in Django .env matches server config
- Check header format: `Authorization: ******
- Restart both Django and vLLM server

---

## Migration Checklist

- [ ] Set up AWS EC2 instance
- [ ] Install dependencies and CUDA
- [ ] Download Llama 3.1 8B model
- [ ] Install and configure vLLM
- [ ] Test inference server locally
- [ ] Create systemd service for auto-restart
- [ ] Update Django code (llm_client.py)
- [ ] Update settings (app_settings.py)
- [ ] Add environment variables
- [ ] Test with sample requests
- [ ] Configure security (firewall, API keys)
- [ ] Set up monitoring
- [ ] Prepare training data for fine-tuning
- [ ] Fine-tune model (optional but recommended)
- [ ] Load test
- [ ] Deploy fine-tuned model
- [ ] Update documentation
- [ ] Monitor costs

---

## Next Steps

1. **Start small:** Test with Groq first, then migrate
2. **Gradual rollout:** Use feature flag to switch 10% traffic to local
3. **Monitor:** Compare quality and performance
4. **Optimize:** Fine-tune based on real usage data
5. **Scale:** Add more instances behind load balancer as needed

---

## Additional Resources

- [vLLM Documentation](https://docs.vllm.ai/)
- [Llama 3.1 Model Card](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct)
- [LoRA Fine-tuning Guide](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora)
- [AWS EC2 GPU Instances](https://aws.amazon.com/ec2/instance-types/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

---

## Support

For issues with this deployment guide, please:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review vLLM logs: `sudo journalctl -u llm-server -f`
3. Consult vLLM GitHub issues
4. Contact your DevOps team

**Last Updated:** May 30, 2026
