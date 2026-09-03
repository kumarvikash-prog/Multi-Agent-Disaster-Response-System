# Multi-Agent Disaster Response System

> Capstone Project built with ❤️.

An intelligent multi-agent framework designed to coordinate disaster response, assess real-time damage, allocate resources, and streamline emergency communications.

---

## 👥 Team Contribution Guidelines & Workflow

To maintain clean code and avoid merge conflicts, **all team members must follow this workflow**. Please read this carefully before writing code!

---

### 🌿 1. Branching Strategy

> **Rule #1: NEVER commit directly to `main`.**  
> The `main` branch is protected and contains only stable, reviewed, working code.

#### Branch Naming Format:

Always create a branch from the latest `main` using this format:

- `feature/<feature-name>` (for new features or modules)
- `fix/<bug-name>` (for fixing bugs or broken code)
- `docs/<doc-update>` (for updating README, documentation, or reports)

**Examples:**

- `feature/disaster-detection-agent`
- `feature/resource-allocation-logic`
- `fix/agent-communication-timeout`
- `docs/setup-instructions`

---

### 🔄 2. Step-by-Step Contribution Steps

Follow these simple Git commands in order:

#### Step 1: Update your local `main`

> 🚨♦️🔴 Always pull the latest changes before starting new work:

```bash
git checkout main
git pull origin main
```

#### Step 2: Create a new branch

```bash
git checkout -b feature/your-feature-name
```

#### Step 3: Work on your changes & commit

Write small, meaningful commits instead of one huge commit:

```bash
git status
git add <files-you-changed>
git commit -m "feat: add initial prompt for damage assessment agent"
```

_Commit message prefixes to use:_

- `feat:` (New feature)
- `fix:` (Bug fix)
- `docs:` (Documentation update)
- `refactor:` (Code restructuring without feature changes)

#### Step 4: Push branch to GitHub

```bash
git push origin feature/your-feature-name
```

#### Step 5: Open a Pull Request (PR)

1. Go to the project repository on GitHub.
2. Click **"Compare & pull request"**.
3. Add a clear title and brief description explaining:
   - What does this PR do?
   - How can teammates test it?
4. Request at least **one team member** to review your code.
5. Once approved and checks pass, merge into `main` and delete the branch.

---

### ✅ 3. What to Do (Best Practices)

- **Pull frequently:** Run `git pull origin main` often to stay updated with your team.
- **Keep PRs small:** Smaller PRs are much easier to review, test, and merge without conflicts.
- **Test locally before pushing:** Make sure your code runs and doesn't crash existing functionality.
- **Use meaningful commit messages:** Say what you did (e.g., `feat: setup fastAPI route for agent query` instead of `changes` or `update`).
- **Communicate with the team:** Mention in group chat if you are touching shared configuration files or shared agent base classes.

---

### ❌ 4. What to Avoid (Strictly Prohibited)

- ❌ **Do NOT push directly to `main` branch.**
- ❌ **Do NOT commit secrets or sensitive data:** Never commit API keys (e.g., Gemini / OpenAI / Map API keys), database credentials, or `.env` files. Always use `.env.example`.
- ❌ **Do NOT commit virtual environments or dependencies:** Never commit `venv/`, `__pycache__/`, or `node_modules/`. (Ensure they are added in `.gitignore`).
- ❌ **Do NOT force push (`git push --force`):** This can overwrite your teammates' work.
- ❌ **Do NOT merge your own PR without review:** Always get another team member to review and approve your code.
- ❌ **Do NOT leave broken code on `main`:** If a feature isn't working yet, keep working on your branch.

---

## 🛠️ Project Setup & Getting Started

_(I will Add setup instructions, environment requirements, and run commands here as the project grows)_
