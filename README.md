# Autonomous Cyber Deception Grid

An AI-driven multi-level honeypot system that deploys adaptive honeypots creating realistic, interactive fake enterprise networks. The system learns attacker behavior in real-time, dynamically evolves its digital landscape to stall threats, and safely maps live adversary tactics.

## Architecture

### Level 1: Static Deception Layer
- Deploy basic mock services (fake SSH, HTTP servers, databases)
- Containerized isolation for mock environments
- Log attacker IPs, timestamps, and input commands

### Level 2: Behavioral AI Adaptation
- Local LLM integration for dynamic responses
- Realistic fake output files and system errors
- Tailored environment based on exploit style

### Level 3: Autonomous Landscape Evolution
- Reinforcement learning for network topology changes
- Dynamic high-value target relocation
- Fake network footprint expansion around aggressive actors

### Level 4: Threat Intelligence & Attribution Sync
- Automated malware sandbox analysis
- MITRE ATT&CK framework mapping
- Central security dashboard integration

## Project Structure

```
cyber-deception-grid/
├── src/
│   ├── core/                   # Core orchestration & shared utilities
│   ├── level1_static/          # Static honeypot services
│   ├── level2_behavioral/      # LLM-driven adaptive responses
│   ├── level3_autonomous/      # RL-based topology evolution
│   ├── level4_intel/           # Threat intelligence & attribution
│   └── api/                    # REST API & dashboard
├── configs/                    # Configuration files
├── docker/                     # Dockerfiles per service
├── k8s/                        # Kubernetes manifests
├── tests/                      # Unit & integration tests
��── docs/                       # Documentation
```

## Quick Start

### Docker Compose (Full Stack)
```bash
docker-compose -f docker/docker-compose.yml up --build
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| ssh-honeypot | 2222 | Fake SSH server |
| http-honeypot | 8080 | Fake HTTP server |
| db-honeypot | 3306 | Fake MySQL database |
| deception-api | 8000 | Main API & orchestration |
| llm-adapter | 8001 | LLM response generation |
| rl-controller | 8002 | RL topology controller |
| intel-processor | 8003 | Threat intelligence |
| dashboard | 3000 | React dashboard |

## Requirements

- Docker & Kubernetes
- Python 3.10+
- Node.js 18+ (for dashboard)
- Ollama or local LLM (for Level 2)
- GPU recommended for RL training