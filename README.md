# CloudOps Simulator: Meta PyTorch Hackathon Submission
Empowering Autonomous Infrastructure Management with Meta Llama-3-70B

## Overview
CloudOps Simulator is a high-fidelity environment designed to train and evaluate AI agents in the domain of Automated DevOps and Infrastructure-as-Code (IaC).

## Technical Stack
- LLM Agent: Meta Llama-3-70B-Instruct
- Framework: OpenEnv (v1.0 compliance)
- Backend: FastAPI for environment communication

## Environment Features
- Action Space: create_instance, create_bucket, upload_file, delete_instance.
- Observation Space: Structured JSON with resource states.

## Compliance
- Logging: Follows [START], [STEP], and [END] formats.
- Hardware: Complies with 2 vCPUs / 8GB RAM limits.

## Deployment
openenv push --repo-id <your-username>/cloudops-meta-simulator
