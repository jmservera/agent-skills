# Agent Skills

This repository contains a collection of skills for AI agents, designed to enhance their capabilities in various tasks. Each skill is implemented as a modular component that can be easily integrated into different agent architectures.

## Available Skills

- transcribe-pdf: A skill that allows agents to extract and transcribe text from PDF documents. This skill utilizes a simple library to extract images from PDFs and then uses the LLM vision capabilities to transcribe the text. To install it inside Copilot CLI, run:

  ```bash
  copilot-cli skill install ./skills
  ```
