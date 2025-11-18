# 🚀 Slack Integrations Offline Pipeline

.....

# 📑 Table of Contents

- [📋 Prerequisites](#-prerequisites)
- [🎯 Getting Started](#-getting-started)
- [📁 Project Structure](#-project-structure)
- [🏗️ Set Up Your Local Infrastructure](#-set-up-your-local-infrastructure)
- [⚡️ Running the Code for Each Module](#️-running-the-code-for-each-module)

# 📋 Prerequisites

## Local Tools

For all the modules, you'll need the following tools installed locally:

| Tool | Version | Purpose | Installation Link |
|------|---------|---------|------------------|
| Python | 3.12 | Programming language runtime | [Download](https://www.python.org/downloads/) |
| uv | ≥ 0.4.30 | Python package installer and virtual environment manager | [Download](https://github.com/astral-sh/uv) |
| Git | ≥2.44.0 | Version control | [Download](https://git-scm.com/downloads) |
| Docker | ≥27.4.0 | Containerization platform | [Download](https://www.docker.com/get-started/) |

<details>
<summary><b>📌 Windows users also need to install WSL for ZenML to run (Click to expand)</b></summary>

You need to **install WSL**, which will install a Linux kernel on your Windows machine to run ZenML pipelines, because ZenML currently does not support windows. 

🔗 [Follow this guide to install WSL](https://www.youtube.com/watch?v=YByZ_sOOWsQ).
</details>

## Cloud Services

Also, the course requires access to these cloud services. The authentication to these services is done by adding the corresponding environment variables to the `.env` file:

| Service | Purpose | Cost | Environment Variable | Setup Guide | Starting with Module |
|---------|---------|------|---------------------|-------------| ---------------------|
| [OpenAI API](https://openai.com/index/openai-api/) | LLM API | Pay-per-use | `OPENAI_API_KEY` | [Quick Start Guide](https://platform.openai.com/docs/quickstart) | Module 2 |

When working locally, the infrastructure is set up using Docker. Thus, you can use the default values found in the [config.py](apps/slack-integrations-offline/src/slack_integrations_offline/config.py) file for all the infrastructure-related environment variables.

But, in case you want to deploy the code, you'll need to setup the following services with their corresponding environment variables:

| Service | Purpose | Cost | Required Credentials | Setup Guide |
|---------|---------|------|---------------------|-------------| 
| [MongoDB](https://rebrand.ly/second-brain-course-mongodb) | document database (with vector search) | Free tier | `MONGODB_URI` | 1. [Create a free MongoDB Atlas account](https://rebrand.ly/second-brain-course-mongodb-setup-1) <br> 2. [Create a Cluster](https://rebrand.ly/second-brain-course-mongodb-setup-2) </br> 3. [Add a Database User](https://rebrand.ly/second-brain-course-mongodb-setup-3) </br> 4. [Configure a Network Connection](https://rebrand.ly/second-brain-course-mongodb-setup-4) |

# 🎯 Getting Started

## 1. Clone the Repository

Start by cloning the repository and navigating to the project directory:
```
git clone https://github.com/karthikponna/slack_integrations.git
cd slack_integrations
```

## 2. Installation

First deactivate any active virtual environment and move to the `slack-integrations-offline` directory:
```bash
deactivate
cd apps/slack-integrations-offline
```

To install the dependencies and activate the virtual environment, run the following commands:

```bash
uv venv .venv-offline
source .venv-offline/bin/activate
uv sync
```

We use [Crawl4AI](https://github.com/unclecode/crawl4ai) for crawling. To finish setting it up you have to run some post-installation setup commands (more on why this is needed in their [docs](https://github.com/unclecode/crawl4ai)):
```bash
# Run post-installation setup
crawl4ai-setup

# Verify your installation
crawl4ai-doctor
```

After running the doctor command, you should see something like this:
```console
[INIT].... → Running Crawl4AI health check...
[INIT].... → Crawl4AI 0.4.247
[TEST].... ℹ Testing crawling capabilities...
[EXPORT].. ℹ Exporting PDF and taking screenshot took 0.84s
[FETCH]... ↓ https://crawl4ai.com... | Status: True | Time: 3.91s
[SCRAPE].. ◆ Processed https://crawl4ai.com... | Time: 11ms
[COMPLETE] ● https://crawl4ai.com... | Status: True | Total: 3.92s
[COMPLETE] ● ✅ Crawling test passed!
```
[More on installing Crawl4AI](https://docs.crawl4ai.com/core/installation/)

## 3. Environment Configuration

Before running any command, you have to set up your environment:
1. Create your environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and configure the required credentials following the inline comments and the recommendations from the [Cloud Services](#-prerequisites) section.

# 📁 Project Structure

```bash
.
├── configs/                   # ZenML configuration files
├── pipelines/                 # ZenML ML pipeline definitions
├── src/slack_integrations_offline/  # Main package directory
│   ├── applications/           # Application layer
│   ├── domain/                # Domain layer
│   ├── infrastructure/        # Infrastructure layer
│   ├── rag/                   # RAG layer
│   ├── config.py              # Configuration settings
│   └── utils.py               # Utility functions
├── steps/                     # ZenML pipeline steps
├── tools/                     # Entrypoint scripts that use the Python package
├── .env.example               # Environment variables template
├── .python-version            # Python version specification
├── Makefile                   # Project commands
└── pyproject.toml             # Project dependencies
```

# 🏗️ Set Up Your Local Infrastructure

We use Docker to set up the local infrastructure (ZenML, MongoDB).

> [!WARNING]
> Before running the command below, ensure you do not have any processes running on port `27017` (MongoDB) and `8237` (ZenML).

To start the Docker infrastructure, run:
```bash
make local-infrastructure-up
```

To stop the Docker infrastructure, run:
```bash
make local-infrastructure-down
```

> [!NOTE]
> To visualize the raw and RAG data from MongoDB, we recommend using [MongoDB Compass](https://rebrand.ly/second-brain-course-mongodb-compass) or Mongo's official IDE plugin (e.g., `MongoDB for VS Code`). To connect to the working MongoDB instance, use the `MONGODB_URI` value from the `.env` file or found inside the [config.py](src/slack_integrations_offline/config.py) file.

[More on setting up `MongoDB for VS Code`](https://youtu.be/gFjpv-nZO0U?si=eGxPeqGN2NfIZg0H)

![mongodb_for_vscode.png](../../static/mongodb_for_vscode.png)

[More on setting up `MongoDB Compass`](https://youtu.be/sSoVyHap3HY?si=IZd_F-hUZfN6-JPk)

![monogdb_compass.png](../../static/monogdb_compass.png)