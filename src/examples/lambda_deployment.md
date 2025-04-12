# AWS Lambda Deployment Guide

This guide explains how to deploy the `lambda_handler.py` file to AWS Lambda for running LLM prompts against multiple providers.

## Prerequisites

- AWS Account with Lambda access
- AWS CLI installed and configured (optional, for command-line deployment)

## Deployment Steps

### 1. Create a Deployment Package

First, create a deployment package including all dependencies:

```bash
# Create a directory for the deployment package
mkdir deployment
cd deployment

# Install dependencies
pip install --target ./package openai-agents openai

# Add your library
cp -r /path/to/your/project/src/llm_compatibility ./package/

# Copy the lambda handler
cp /path/to/your/project/src/examples/lambda_handler.py ./package/

# Create a ZIP file
cd package
zip -r ../lambda_deployment.zip .
cd ..
```

### 2. Create Lambda Function

#### Using AWS Console

1. Go to the AWS Lambda console
2. Click "Create function"
3. Choose "Author from scratch"
4. Enter a function name (e.g., `llm-compatibility-function`)
5. Select Python 3.9 or higher as the runtime
6. Click "Create function"
7. In the "Code" tab, upload the `lambda_deployment.zip` file
8. Set the handler to `lambda_handler.lambda_handler`

#### Using AWS CLI

```bash
aws lambda create-function \
  --function-name llm-compatibility-function \
  --runtime python3.9 \
  --role arn:aws:iam::your-account-id:role/lambda-execution-role \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://lambda_deployment.zip
```

### 3. Configure Environment Variables

In the Lambda console, go to the "Configuration" tab, then "Environment variables", and add the following:

| Key                 | Value (example)                             | Description                       |
| ------------------- | ------------------------------------------- | --------------------------------- |
| `SYSTEM_PROMPT`     | "You are a helpful weather assistant."      | System prompt/instructions        |
| `USER_MESSAGE`      | "What's the weather like in San Francisco?" | Default user message              |
| `PROVIDERS`         | "openai,claude"                             | Comma-separated list of providers |
| `MODEL_NAME_OPENAI` | "gpt-4o-2024-08-06"                         | Model for OpenAI                  |
| `MODEL_NAME_CLAUDE` | "claude-3-haiku-20240307"                   | Model for Claude                  |
| `API_KEY_OPENAI`    | "sk-..."                                    | API key for OpenAI                |
| `API_KEY_CLAUDE`    | "sk-..."                                    | API key for Claude                |
| `TEMPERATURE`       | "0.7"                                       | Temperature parameter             |

### 4. Configure Lambda Settings

- Set timeout to at least 30 seconds (LLM calls can take time)
- Adjust memory as needed (256MB should be sufficient)

### 5. Testing the Function

You can test the function with a test event like:

```json
{
  "message": "What's the weather in New York?",
  "providers": ["openai", "claude"],
  "temperature": 0.8
}
```

Or let it use the environment variable defaults by providing an empty event:

```json
{}
```

### 6. Creating an API Endpoint (Optional)

To expose your Lambda as an API:

1. Go to API Gateway in the AWS Console
2. Create a new REST API
3. Create a new resource and method (e.g., POST)
4. Connect it to your Lambda function
5. Deploy the API

## Function Customization

To customize the Lambda function:

1. Modify the `get_weather` tool or add more tools in the `lambda_handler.py` file
2. Update the deployment package and redeploy

## Security Considerations

- Store API keys securely using AWS Secrets Manager or Parameter Store for production
- Consider adding authentication to your API Gateway endpoint
- Review IAM permissions for your Lambda function
