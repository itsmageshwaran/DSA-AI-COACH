---
title: Dsa Ai Coach Backend
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# DSA AI Coach - Personalized Mastery System

Welcome to the **Personalized DSA Career Mastery Coach**. This application is an end-to-end learning platform that provides personalized DSA (Data Structures & Algorithms) curriculum pathways tailored to specific software engineering careers (Backend, Frontend, ML/AI, Cybersecurity, etc.).

## 🚀 Key Features

*   **Career-Oriented Roadmaps**: Curriculum dynamically adjusts priority concepts based on your selected career path.
*   **Progressive Mastery**: Deterministic difficulty scaling. Starts you at Easy and logically promotes you to Medium and Hard based on your actual pass rates and mastery scores.
*   **Real Code Execution**: Integrated python runtime for executing submissions against strict test cases in an isolated environment.
*   **AI Tutoring**: Integrated NVIDIA NIM AI that understands your code and provides Socratic feedback without giving away the answers.
*   **Curriculum Engine**: 25 highly curated, executable problems seeded directly into PostgreSQL.
*   **Premium UX**: "Calm Intelligence" UI aesthetic with Monaco Editor.

## 🛠️ Tech Stack

*   **Frontend**: React, TypeScript, Vite, TailwindCSS, Zustand, Monaco Editor.
*   **Backend**: Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, Poetry.
*   **AI/Execution**: NVIDIA NIM, Isolated AST-validated subprocess execution.

## 🏃‍♂️ Getting Started

The entire stack is containerized for simple, reliable onboarding.

See DOCKER_SETUP.md for complete setup instructions!

## 📚 Curriculum

See CURRICULUM.md for a complete breakdown of the dynamic learning graph.
