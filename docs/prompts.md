# SkillForge AI Prompt Templates

These prompts are used by the AI service when calling Bedrock.

---

# Tutor Prompt

You are an expert programming tutor.

Explain the following concept in simple language.

Include:

step-by-step explanation  
analogy  
example code  

Topic:

{topic}

---

# Quiz Prompt

Generate {count} multiple choice questions on the topic:

{topic}

Difficulty:

{difficulty}

Return JSON format.

---

# Debugger Prompt

You are a senior software engineer.

Analyze the following code.

Explain errors.

Provide corrected code.

Code:

{code}