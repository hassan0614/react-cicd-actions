import os
import requests
import openai
import subprocess

# Load secrets from GitHub Actions env
openai.api_key = os.getenv("OPENAI_API_KEY")
pr_number = os.getenv("PR_NUMBER")
repo = os.getenv("GITHUB_REPOSITORY")
github_token = os.getenv("GITHUB_TOKEN")

# Step 1: Get PR Diff using Git
def get_pr_diff():
    try:
        diff = subprocess.check_output(["git", "diff", "origin/main...HEAD"], text=True)
        return diff
    except subprocess.CalledProcessError as e:
        print("Failed to get diff:", e)
        return ""

# Step 2: Ask GPT to explain the diff
def ask_gpt(diff_text):
    prompt = f"""
You are a senior software engineer. Here is a GitHub Pull Request diff:

{diff_text}

Please summarize what changes have been made in plain English, including:
- What functionality was added/modified/removed?
- Any potential issues or improvements?
- Summarize the purpose of this PR.

Be detailed and developer-friendly.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",  # You can switch to "gpt-3.5-turbo" if needed
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response["choices"][0]["message"]["content"]

# Step 3: Post a comment on the PR
def post_pr_comment(body_text):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"body": body_text}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("Comment posted successfully.")
    else:
        print(f"Failed to post comment: {response.status_code}")
        print(response.text)

# Main script
if __name__ == "__main__":
    print("Fetching diff...")
    diff = get_pr_diff()

    if diff.strip() == "":
        post_pr_comment("No code changes detected in this PR.")
    else:
        print("Generating explanation...")
        explanation = ask_gpt(diff)
        post_pr_comment(f"### 🤖 PR Summary by AI:\n{explanation}")
