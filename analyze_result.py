import json
import os
from github import Github

def get_sonarqube_issues():
    with open('sonarqube-report.json', 'r') as f:
        data = json.load(f)
    return data['issues']

def get_dependency_check_vulnerabilities():
    with open('dependency-check-report.json', 'r') as f:
        data = json.load(f)
    return data['dependencies']

def analyze_results():
    sonar_issues = get_sonarqube_issues()
    vulnerabilities = get_dependency_check_vulnerabilities()

    code_smells = [issue for issue in sonar_issues if issue['type'] == 'CODE_SMELL']
    bugs = [issue for issue in sonar_issues if issue['type'] == 'BUG']
    vulnerabilities_high_severe = [v for v in vulnerabilities if v['severity'] in ['HIGH', 'CRITICAL']]

    outdated_dependencies = [d for d in vulnerabilities if 'outdated' in d]

    feedback = f"""
## Code Quality and Security Analysis Results

### Code Quality (SonarQube):
- Code Smells: {len(code_smells)}
- Bugs: {len(bugs)}

### Security (OWASP Dependency-Check):
- High/Severe Vulnerabilities: {len(vulnerabilities_high_severe)}
- Outdated Dependencies: {len(outdated_dependencies)}

"""

    if code_smells:
        feedback += "\n### Code Smells:\n"
        for smell in code_smells[:5]:  # List top 5 code smells
            feedback += f"- {smell['message']} (Line: {smell['line']})\n"

    if bugs:
        feedback += "\n### Bugs:\n"
        for bug in bugs[:5]:  # List top 5 bugs
            feedback += f"- {bug['message']} (Line: {bug['line']})\n"

    if vulnerabilities_high_severe:
        feedback += "\n### High/Severe Vulnerabilities:\n"
        for vuln in vulnerabilities_high_severe[:5]:  # List top 5 vulnerabilities
            feedback += f"- {vuln['description']} (Severity: {vuln['severity']})\n"

    if outdated_dependencies:
        feedback += "\n### Outdated Dependencies (Warnings):\n"
        for dep in outdated_dependencies[:5]:  # List top 5 outdated dependencies
            feedback += f"- {dep['fileName']} (Current: {dep['version']}, Latest: {dep['latestVersion']})\n"

    status = "failure" if vulnerabilities_high_severe else "success"

    return feedback, status

def update_pr_status(feedback, status):
    github_token = os.environ['GITHUB_TOKEN']
    repo_name = os.environ['GITHUB_REPOSITORY']

    g = Github(github_token)
    repo = g.get_repo(repo_name)

    # Get the most recent pull request
    pr = repo.get_pulls(state='open', sort='updated', direction='desc')[0]

    # Post feedback as a comment on the PR
    pr.create_issue_comment(feedback)
    
    # Update the commit status
    commit = repo.get_commit(pr.head.sha)
    commit.create_status(
        state=status,
        target_url=f"https://github.com/{repo_name}/actions",
        description="Code quality and security checks",
        context="codebuild/pr-check"
    )

if __name__ == "__main__":
    feedback, status = analyze_results()
    with open('pr_feedback.md', 'w') as f:
        f.write(feedback)
    update_pr_status(feedback, status)