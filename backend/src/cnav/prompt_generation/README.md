# Cyber Essentials Evaluation Prompt Generator

This module generates evaluation prompts for auditors to assess organization compliance with Singapore Cyber Essentials certification provisions.

## Overview

The Cyber Essentials mark is a baseline cybersecurity certification designed for organizations with limited IT and cybersecurity expertise. This tool generates detailed evaluation prompts that auditors can use to assess whether an organization's self-assessment response demonstrates compliance with specific cybersecurity provisions.

## Setup

1. **Install dependencies**:
   ```bash
   cd backend
   uv sync
   ```

2. **Set up environment variables**:
   Create a `.env` file in the `backend` directory with:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Prepare data**:
   Ensure you have the structured cyber essentials data in:
   ```
   backend/src/data/cyber-essentials-structured.json
   ```

## Usage

Run the prompt generation script:

```bash
cd backend/src/prompt_generation
uv run main.py
```

The script will:
1. Create a timestamped output directory (format: `YYYYMMDDHHMMSS`)
2. Load the structured cyber essentials data
3. Create a LangChain chain with GPT-4o-mini
4. Generate evaluation prompts for each clause-provision pair
5. Save each prompt immediately as an individual `.md` file
6. Create an index.md file for easy navigation
7. Save a summary JSON file with all results

## Output Format

The script creates a timestamped directory in `./output/YYYYMMDDHHMMSS/` containing:

### Individual Prompt Files
Each provision gets its own markdown file with snake_case naming:
- `a_1_4_a.md` (for provision A.1.4 (a))
- `a_2_4_b.md` (for provision A.2.4 (b))
- etc.

Each markdown file contains:
```markdown
# Evaluation Prompt for A.1.4 (a)

## Clause Information
**Clause ID**: A.1 Assets: People – Equip employees...

## Provision ID
A.1.4 (a)

## Evaluation Prompt

[Generated evaluation prompt content]

---
*Generated on: 2024-01-01 12:00:00*
```

### Index File
`index.md` - Navigation file listing all generated prompts organized by clause

### Summary File
`generation_summary.json` - Complete results in JSON format for programmatic access

## Configuration

The script uses the following LangChain configuration:
- **Model**: GPT-4o-mini
- **Temperature**: 0.1 (for consistent, focused outputs)
- **Max tokens**: 2000 (sufficient for detailed evaluation prompts)

## System Prompt

The system prompt instructs the AI to act as an expert cybersecurity auditor specializing in the Singapore Cyber Essentials certification framework. It emphasizes:

- Practical evaluation criteria
- Resource constraints of typical applicants
- Specific evidence requirements
- Clear compliance vs non-compliance definitions
- Common pitfalls and misunderstandings

## Error Handling

The script includes comprehensive error handling:
- Continues processing even if individual provisions fail
- Logs errors for failed generations
- Provides a summary of successful vs failed generations
- Saves partial results even with errors

## Dependencies

- `langchain>=0.3.26`
- `langchain-openai>=0.3.27`
- `python-dotenv>=1.0.0`
- OpenAI API key with sufficient credits 