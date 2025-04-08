# 🧠 Multi-Agent AI Orchestration Framework

This project is a proof-of-concept for an event-driven multi-agent orchestration framework that uses Kafka and CloudEvents to manage collaborative AI agents (e.g., app design, Terraform generation, Kafka architecture advice) in a modular and decoupled way.

---

## 🚀 Key Features

- 🧱 Modular AI agents (App Designer, Terraform Generator, Kafka Expert)
- ⚙️ Core framework to coordinate multi-step workflows
- 📬 Event-driven with **Kafka + CloudEvents**
- 🧾 Workflow configuration via YAML or JSON
- 📦 State persistence via MongoDB
- 🔁 Asynchronous processing across microservices
- 🌐 Supports HTTP-based or local agents as well

---

## 🧩 Architecture Overview

```mermaid
graph TD
    User["User Request"] -->|workflow.request| Kafka[Kafka Broker]
    Kafka -->|dispatch| Framework[Orchestration Engine]
    Framework -->|invoke| AppDesigner[App Designer Agent (HTTP)]
    Framework -->|publish| Kafka
    Kafka --> TerraformAgent[Terraform Agent (Kafka)]
    Kafka --> KafkaExpertAgent[Kafka Expert Agent (Kafka)]
    Kafka -->|workflow.output| OutputLogger[Workflow Output Logger]
    Framework --> MongoDB[MongoDB (state)]
```

---

## 📂 Project Structure

```bash
.
├── framework/            # Core engine: orchestrator, event loop, handlers
├── agents/               # All agent code (app_designer, terraform, kafka)
├── runner/               # Scripts to trigger workflows
├── docker-compose.yml    # Local dev stack
├── Dockerfile.*          # One per service type
├── requirements.txt      # Common Python deps
```

---

## 🧪 Running Locally

### 1. Start the full system:
```bash
docker compose up --build
```

### 2. Send a workflow request:
```bash
python framework/runner/send_workflow_request.py
```

### 3. Tail logs:
```bash
./tail_all_logs.sh
```

---

## 📦 Services

| Service             | Description                          | Protocol |
|--------------------|--------------------------------------|----------|
| `app-designer`     | HTTP microservice AI agent           | HTTP     |
| `terraform-agent`  | Kafka microservice AI agent          | Kafka    |
| `kafka-expert`     | Kafka microservice AI agent          | Kafka    |
| `framework-core`   | Orchestration engine + event router  | Kafka    |

---

## 📬 Topics Used

| Topic                               | Description                          |
|------------------------------------|--------------------------------------|
| `workflow.request`                 | Initial workflow entry point         |
| `workflow.step.response`           | Agent step completion notification   |
| `workflow.step.{name}.request`     | Per-step request dispatch topic      |
| `workflow.output`                  | Final result of workflow             |

---

## 🔐 Environment Variables

| Variable              | Purpose                              |
|-----------------------|--------------------------------------|
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka connection string          |
| `MONGODB_URI`         | MongoDB connection string            |
| `OPENAI_API_KEY`      | API Key for LLM agent calls          |

---

## 📘 Future Improvements

- [ ] Parallel branches & conditional flows
- [ ] Secure agent registry and permissions
- [ ] External user-facing notification API
- [ ] Retry, error handling, and timeouts

---

## 📣 Contact
Made with ❤️ for experimentation and extensibility. Contributions welcome!

