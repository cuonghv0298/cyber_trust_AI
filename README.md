# CNAV
Using LLM chain: Just process plain text
# Next step
- AI API endpoints (POST METHOD): [source](/home/kdts33/Cuonghv/delivery/cnav/backend/src/cnav/__main__.py)
1. SYSTEM_PROMPT_DIR => read from /home/kdts33/Cuonghv/delivery/cnav/backend/src/cnav/prompt_generation/output/20250813040201/generation_summary.json => run /home/kdts33/Cuonghv/delivery/cnav/backend/src/cnav/prompt_generation/metaprompting_pipeline.py => list of **mds**.
2. DATABASE_URL: get questions / provisions 
3. FIXED ORGANIZATION: "Rotary"

Development process for the evident: 
4. Dev evident: /home/kdts33/Cuonghv/delivery/cnav/backend/src/cnav/prompts/main_user_prompt.py 
    > Add field: {evident} = field(str, ....)
5. Dev run_evaluation: 
    > Format adaptation 
    > IE from evident
