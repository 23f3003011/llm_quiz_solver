services:
  - type: web
    name: llm-quiz-solver
    runtime: python
    plan: free
    buildCommand: bash build.sh
    startCommand: python main.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: PORT
        value: "5000"
