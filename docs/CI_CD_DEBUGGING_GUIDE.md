# 🚀 CI/CD Debugging Guide for Beginners

## 📚 What is CI/CD and Why Does It Matter?

### **CI (Continuous Integration)**
- **What it does**: Automatically runs tests, checks code quality, and builds your project **every time you push code** to GitHub
- **Why it matters**: 
  - Catches bugs **before** they reach production
  - Ensures code works on a clean server (not just your computer)
  - Helps teammates know if their changes broke something
  - Gives you confidence your code works

### **CD (Continuous Deployment)**
- **What it does**: Automatically deploys your code to production when tests pass
- **Why it matters**: 
  - No manual deployment steps
  - Faster releases
  - Consistent deployment process

### **Think of CI/CD as a Robot Assistant**
- Every time you push code → Robot runs your tests
- If tests pass → Robot says "✅ All good!"
- If tests fail → Robot says "❌ Something broke at line X, here's why..."
- Robot can also deploy your code automatically (if you set it up)

---

## 🛠️ How to Use GitHub Actions (Your CI/CD Tool)

### **Where is CI/CD configured?**
- Location: `.github/workflows/` directory in your repo
- Files: YAML files (`.yml` or `.yaml`) that describe what to run
- Example: `.github/workflows/django.yml` tells GitHub: "When someone pushes code, run Django tests"

### **How GitHub Actions Works**
1. **Trigger**: You push code → GitHub detects it
2. **Checkout**: GitHub downloads your code to a clean virtual machine
3. **Setup**: Installs Python, dependencies, etc.
4. **Run**: Executes your tests/commands
5. **Report**: Shows you ✅ or ❌ in the GitHub UI

---

## 🔍 Debugging CI/CD Failures: Step-by-Step Workflow

### **Step 1: Understand the Error Message**

When CI fails, GitHub shows you:
- ❌ **Red X** on the commit
- **Job logs** - Click to see detailed error messages
- **Which workflow failed** - The name of the YAML file

**Common Error Types:**
- `FileNotFoundError` → Missing file/directory
- `ImportError` → Python can't find a module
- `ModuleNotFoundError` → Package not installed
- `SyntaxError` → Code has a typo
- `AssertionError` → Test failed

### **Step 2: Reproduce Locally First**

**Before asking AI tools for help, try to reproduce the error:**

```bash
# 1. Get the exact commit that failed
git checkout <commit-hash-from-failure>

# 2. Create a clean environment (like CI does)
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# OR test_env\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the same command CI runs
python manage.py test
# OR
pytest
# OR whatever command is in your workflow file
```

**If you can reproduce it locally:**
- ✅ Great! You can debug locally with faster feedback
- Fix it locally, then push → CI should pass

**If you CAN'T reproduce locally:**
- ❌ Likely a CI environment issue (missing file, wrong path, etc.)
- This is where AI tools help most!

### **Step 3: Gather Context for AI Tools**

**Before asking Cursor/ChatGPT/Claude, collect:**

1. **The exact error message** (copy from GitHub Actions logs)
   ```
   FileNotFoundError: No such file or directory: 'agent_core/'
   ```

2. **The workflow file** (`.github/workflows/django.yml`)
   - Copy the entire file content

3. **The repository structure**
   ```bash
   # Run this and share output
   find . -type d -name "*agent_core*" -print
   ls -la apps/
   ```

4. **The commit hash** that failed
   ```
   57cb7c337380ff1e6e3fb2b7c75db7cebba3d4ad
   ```

5. **What you expect** vs **what happened**
   - Expected: `agent_core` should be found
   - Actual: CI can't find `agent_core/`

### **Step 4: Ask AI Tools the Right Way**

#### **❌ Bad Question (Too Vague):**
> "My CI is broken, help!"

#### **✅ Good Question (Specific & Actionable):**
> "GitHub Actions CI fails at commit 57cb7c337380ff1e6e3fb2b7c75db7cebba3d4ad with error:
> 
> `FileNotFoundError: No such file or directory: 'agent_core/'`
> 
> My workflow file:
> ```yaml
> [paste workflow content]
> ```
> 
> My repo structure: `agent_core` is located at `apps/agent_core/`, not at root `agent_core/`
> 
> The test file imports: `from apps.agent_core import ...`
> 
> Question: Should I update the workflow to set PYTHONPATH or change how tests are run? Show exact code changes."

---

## 🤖 How to Use Each AI Tool Effectively

### **Cursor (This Tool)**

**Best for:**
- ✅ Analyzing your actual codebase
- ✅ Making code changes directly
- ✅ Understanding file structure
- ✅ Finding where imports are used

**How to use:**
1. Open the file that's failing in Cursor
2. Ask: "Why does CI fail with FileNotFoundError for agent_core?"
3. Cursor can read your actual files and suggest fixes
4. Review suggestions → Apply if they make sense

**Example prompt:**
```
My CI workflow expects agent_core/ at root, but it's at apps/agent_core/. 
Show me the exact changes needed in .github/workflows/django.yml to fix this.
Make sure PYTHONPATH includes the repo root so Django can find apps.agent_core.
```

### **ChatGPT / Claude**

**Best for:**
- ✅ Explaining CI/CD concepts
- ✅ Debugging YAML syntax
- ✅ Understanding error messages
- ✅ Getting general guidance

**How to use:**
1. Paste the error message
2. Paste your workflow file
3. Ask: "What's wrong and how do I fix it?"
4. Ask follow-up: "Show me the exact YAML changes"

**Example prompt:**
```
[Paste error]
[Paste workflow file]
[Paste repo structure]

This is a Django project. The agent_core package is at apps/agent_core/, 
not root. How should I configure the workflow to:
1. Set PYTHONPATH correctly
2. Run Django tests
3. Install dependencies from requirements.txt

Show exact YAML changes.
```

---

## 🐛 Common CI/CD Issues & Fixes

### **Issue 1: FileNotFoundError: agent_core/**

**Root Cause:**
- CI expects `agent_core/` at root, but it's at `apps/agent_core/`
- Python can't find the module because PYTHONPATH isn't set

**Fix:**
```yaml
- name: Set PYTHONPATH
  run: echo "PYTHONPATH=${{ github.workspace }}" >> $GITHUB_ENV
```

### **Issue 2: ImportError: No module named 'apps'**

**Root Cause:**
- Django settings use `apps.agent_core` but Python doesn't know where `apps` is

**Fix:**
```yaml
- name: Install package in development mode
  run: pip install -e .
```

OR set PYTHONPATH:
```yaml
- name: Add repo root to PYTHONPATH
  run: |
    echo "PYTHONPATH=${{ github.workspace }}" >> $GITHUB_ENV
    echo "PYTHONPATH is set to: $PYTHONPATH"
```

### **Issue 3: Missing Environment Variables**

**Root Cause:**
- Tests need `DJANGO_SECRET_KEY` or other env vars

**Fix:**
```yaml
- name: Set environment variables
  env:
    DJANGO_SECRET_KEY: test-secret-key-for-ci
    DJANGO_DEBUG: "True"
  run: python manage.py test
```

### **Issue 4: Tests Pass Locally but Fail in CI**

**Common Causes:**
1. Missing dependencies in `requirements.txt`
2. Different Python version
3. Missing files (check `.gitignore`)
4. Path differences (Windows vs Linux)

**Debug Steps:**
```yaml
- name: Debug workspace
  run: |
    echo "Python version:"
    python --version
    echo "Current directory:"
    pwd
    echo "Files in repo:"
    ls -la
    echo "Python path:"
    python -c "import sys; print('\n'.join(sys.path))"
    echo "Can we import Django?"
    python -c "import django; print(django.__version__)"
```

---

## 📋 Complete GitHub Actions Workflow Template

Here's a working template for your Django project:

```yaml
name: Django CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    # Step 1: Checkout code (get all files)
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Get full history (important for submodules)
    
    # Step 2: Set up Python
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    
    # Step 3: Install dependencies
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    # Step 4: Set PYTHONPATH (CRITICAL for apps/agent_core structure)
    - name: Set PYTHONPATH
      run: |
        echo "PYTHONPATH=${{ github.workspace }}" >> $GITHUB_ENV
        echo "PYTHONPATH set to: $PYTHONPATH"
    
    # Step 5: Debug (optional - remove after fixing)
    - name: Debug workspace
      run: |
        echo "Workspace: ${{ github.workspace }}"
        echo "Files:"
        ls -la
        echo "Apps directory:"
        ls -la apps/ || echo "apps/ not found"
        echo "Python can find apps:"
        python -c "import sys; sys.path.insert(0, '.'); from apps import agent_core; print('✅ Import successful')" || echo "❌ Import failed"
    
    # Step 6: Run migrations (if needed)
    - name: Run migrations
      env:
        DJANGO_SECRET_KEY: test-secret-key-for-ci-only
        DJANGO_DEBUG: "True"
      run: |
        python manage.py migrate --noinput
    
    # Step 7: Run tests
    - name: Run tests
      env:
        DJANGO_SECRET_KEY: test-secret-key-for-ci-only
        DJANGO_DEBUG: "True"
      run: |
        python manage.py test
    
    # Step 8: Run linting (optional)
    - name: Run flake8
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

---

## 🎯 Quick Debugging Checklist

When CI fails, ask yourself:

- [ ] **Can I reproduce it locally?**
  - If YES → Fix locally, push again
  - If NO → Continue to next questions

- [ ] **Is the file/directory actually in the repo?**
  ```bash
  git ls-files | grep agent_core
  ```

- [ ] **Is it in `.gitignore`?**
  ```bash
  cat .gitignore | grep agent_core
  ```

- [ ] **Is the path correct in the workflow?**
  - Check workflow file paths match your repo structure

- [ ] **Are dependencies installed?**
  - Check `requirements.txt` has everything needed

- [ ] **Is PYTHONPATH set correctly?**
  - Django needs to find `apps.agent_core`

- [ ] **Are environment variables set?**
  - Check if tests need `DJANGO_SECRET_KEY` etc.

---

## 🚀 Best Practices for CI/CD

1. **Test Locally First**
   - Always run tests before pushing
   - Use same Python version as CI

2. **Keep CI Fast**
   - Don't run slow operations (like full database migrations)
   - Cache dependencies when possible

3. **Make CI Failures Obvious**
   - Use clear error messages
   - Add debug steps when troubleshooting

4. **Fix CI Issues Immediately**
   - Don't accumulate broken CI
   - Fix before merging new code

5. **Use Branch Protection**
   - Require CI to pass before merging
   - Prevents broken code from reaching main

---

## 📞 When to Ask for Help

**Ask AI/Cursor/ChatGPT/Claude when:**
- ✅ You've tried reproducing locally but can't
- ✅ You understand the error but don't know how to fix it
- ✅ You need help understanding CI/CD concepts
- ✅ You want to verify your workflow file is correct

**Share these details:**
1. Exact error message
2. Workflow file content
3. Relevant code files (test file, import statements)
4. What you've already tried
5. What you expect vs what happens

---

## 💡 Next Steps

1. **Review this guide** - Understand CI/CD basics
2. **Check your current workflow** - See if `.github/workflows/` exists
3. **Reproduce the error locally** - Try the steps above
4. **Ask Cursor/ChatGPT** - Use the templates above
5. **Apply fixes** - Test locally, then push

---

## 🔗 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Django Testing Guide](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

**Remember**: CI/CD failures are learning opportunities! Each failure teaches you more about how your code works in different environments. 🎓

