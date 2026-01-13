# Secure Serverless URL Shortener (AWS + Terraform)

A security-focused serverless URL shortener built on AWS using Infrastructure as Code (Terraform).  
The project demonstrates real-world cloud security principles including least-privilege IAM, JWT authentication, encryption at rest, API throttling, and observability — all within AWS Free Tier constraints.

---

## 🏗️ Architecture Overview

**Technologies used**
- **AWS Lambda** – serverless backend
- **Amazon API Gateway (HTTP API)** – public API with throttling
- **Amazon Cognito** – JWT authentication
- **Amazon DynamoDB** – encrypted NoSQL storage
- **AWS IAM** – least-privilege roles and policies
- **Amazon CloudWatch** – logs and observability
- **Terraform** – infrastructure as code with remote state & locking

**High-level flow**
1. Client authenticates via Cognito and receives a JWT
2. Authenticated requests call `POST /shorten`
3. API Gateway validates JWT
4. Lambda stores/retrieves URL mappings in DynamoDB
5. `GET /{code}` redirects publicly to the target URL

---

## 🔐 Security Features

- **JWT Authentication**
  - `POST /shorten` protected using Cognito JWT authorizer
  - Unauthenticated requests are rejected (401)
- **Least-Privilege IAM**
  - Lambda role restricted to only required DynamoDB and CloudWatch actions
- **Encryption at Rest**
  - DynamoDB tables encrypted using AWS-managed KMS keys
- **API Throttling**
  - Rate and burst limits configured in API Gateway to mitigate abuse
- **Execution Hardening**
  - Lambda timeout and memory limits enforced
- **Observability**
  - Structured API Gateway access logs
  - CloudWatch log retention configured

---
Response
## 🧪 API Endpoints

### `POST /shorten` (Authenticated)
Creates a short URL.

**Request**
```json
{
  "url": "https://example.com"
}
