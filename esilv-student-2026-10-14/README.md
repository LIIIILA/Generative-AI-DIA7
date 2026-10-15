# Trustworthy Generative AI — Lab Sessions (TD 1 to 3)

## 1. Sub-group Identification & Members

* **Sub-group**: [Numéro / Nom de votre sous-groupe, ex: Sub-group 4]
* **Members**:
  1. [Prénom Nom 1] - `prenom.nom1@edu.devinci.fr` (Role A: Model Batch 1 - Groq)
  2. [Prénom Nom 2] - `prenom.nom2@edu.devinci.fr` (Role B: Model Batch 2 - Groq)
  3. [Prénom Nom 3] - `prenom.nom3@edu.devinci.fr` (Role C: Model Batch 4 - OpenRouter Account 1)
  4. [Prénom Nom 4] - `prenom.nom4@edu.devinci.fr` (Role D: Model Batch 3 - Groq)
  5. [Prénom Nom 5] - `prenom.nom5@edu.devinci.fr` (Role E: Model Batch 5 - OpenRouter Account 2)
  6. [Prénom Nom 6] - `prenom.nom6@edu.devinci.fr` (Role F: Cross-checking & Consolidation)
  7. [Prénom Nom 7] - `prenom.nom7@edu.devinci.fr` (Role G: Traces & Summary Tables)
  8. [Prénom Nom 8] - `prenom.nom8@edu.devinci.fr` (Role H: Traces & Report Preparation)

---

## 2. Course Pack Version & Environment

* **Course Pack Version**: Student Kit dated **14 October 2026** (`esilv-student-2026-10-14` / `kit-td1`)
* **Authorized Models Specification**: `modeles-autorises.json` (Dated `2026-10-14`)
* **Operating System**: Windows 11 / WSL 2 (Ubuntu 24.04 LTS)
* **Python Version**: Python 3.10+ (tested and verified on Python 3.14.x)
* **Dependencies**: `requests`, `sqlite3` (built-in standard library)
* **Providers & Free Routes**:
  * **Groq (Free plan)**:
    * `openai/gpt-oss-120b`
    * `openai/gpt-oss-20b`
    * `qwen/qwen3.8-27b`
  * **OpenRouter (Free tier with `:free` suffix)**:
    * `cohere/north-mini-code:free`
    * `dots-studio/dots-3-note-preview:free`

---

## 3. Setup and Reproduction Commands

Follow the steps below to reproduce our environment, tests, and execution runs.

### A. Environment Setup

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/](https://github.com/)<votre-nom>/<votre-repo>.git
   cd <votre-repo>
