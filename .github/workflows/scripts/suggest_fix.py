import os
import subprocess
import openai

openai.api_key = os.environ["OPENAI_API_KEY"]

# Get merge conflict diff
diff_output = subprocess.getoutput("git diff")

# Request AI suggestion
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You're a helpful assistant that resolves git merge conflicts."},
        {"role": "user", "content": f"Here is a git merge conflict:\n{diff_output}\nPlease suggest a fix."}
    ]
)

suggestion = response['choices'][0]['message']['content']
print("AI Suggestion:\n", suggestion)

# Use GitHub CLI to comment on PR
pr_number = os.environ["PR_NUMBER"]
subprocess.run([
    "gh", "pr", "comment", str(pr_number),
    "--body", suggestion
])
