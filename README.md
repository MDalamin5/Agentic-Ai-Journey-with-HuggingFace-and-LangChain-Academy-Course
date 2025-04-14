# Agentic AI with Hugging Face Course

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

Welcome to the **Agentic AI with Hugging Face Course** repository! This project contains my hands-on work, notes, and experiments from Hugging Face's [Agentic AI course](https://huggingface.co/learn/agents-course/unit0/introduction), which explores the creation, customization, and deployment of LLM-powered agents.

---

## 📚 Course Overview

The course covers:
- Introduction to LLM Agents
- Creating and using tools with `transformers-agents`
- Planning and multi-step reasoning
- Deploying agents using Hugging Face APIs
- Building your own custom agents

> 📎 Link to course: [Hugging Face Agentic AI Course](https://huggingface.co/learn/agents-course/unit0/introduction)

---

## 📂 Repository Structure

```
Agentic-Ai-with-HuggingFace-Course/
├── notebooks/              # Jupyter notebooks per course unit
├── scripts/                # Python scripts and experiments
├── assets/                 # Images or diagrams
├── requirements.txt        # Python dependencies
├── .gitignore              # Ignored files and directories
└── README.md               # This file
```

---

## 🛠️ Setup Instructions

```bash
# Clone the repository
$ git clone https://github.com/MDalamin5/Agentic-Ai-with-HuggingFace-Course.git
$ cd Agentic-Ai-with-HuggingFace-Course

# (Optional) Create and activate a virtual environment
$ python -m venv venv
$ source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
$ pip install -r requirements.txt
```

> 🔐 You may need a Hugging Face API token for agent execution. Visit [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) to create one.

---

## 📓 Course Progress & Notebooks

| Unit | Title                            | Notebook                         |
|------|----------------------------------|----------------------------------|
| 0    | Introduction                     | `notebooks/unit0_intro.ipynb`    |
| 1    | Your First Agent                 | `notebooks/unit1_first_agent.ipynb` |
| 2    | Tools & Tool Use                 | `notebooks/unit2_tools.ipynb`    |
| 3    | Planning with Agents             | `notebooks/unit3_planning.ipynb` |
| 4    | Custom Agents & Deployment       | `notebooks/unit4_custom_agents.ipynb` |

---

## 🧪 Experiments

This section includes custom tools, workflows, and modified agent architectures that go beyond the course exercises.

- `scripts/custom_tool_example.py`
- `scripts/agent_with_memory.py`

---

## 📌 Key Takeaways

- Understand the architecture of agentic systems using LLMs
- Leverage `transformers-agents` to create and register tools
- Use agents for dynamic, multi-step problem-solving
- Customize agents for specific tasks and deployment scenarios

---

## 📜 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

---

## 🙌 Acknowledgments

- [Hugging Face](https://huggingface.co) for providing an awesome open-source ecosystem
- Hugging Face team for the Agentic AI course
- All contributors to `transformers` and `transformers-agents`

---

Happy agent building! 🤖✨