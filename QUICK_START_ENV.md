# Quick Start: Environment Setup

## TL;DR

```bash
# 1. Copy the example file
cp .env.example .env

# 2. Add your API key (get from: https://console.anthropic.com/)
echo "ANTHROPIC_API_KEY=your_actual_api_key_here" > .env

# 3. Verify it works
python3 check_env.py

# 4. Run the app
streamlit run app.py
```

## That's it! 🎉

If `check_env.py` shows all green checkmarks (✓), you're ready to go.

## Troubleshooting

**Problem:** Script says "ANTHROPIC_API_KEY is NOT set"

**Solution:**
```bash
# Make sure .env file exists
ls -la .env

# Make sure it has your key
cat .env
# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

**Problem:** Everything else

**Solution:** See the comprehensive guide:
- [ENV_SETUP_GUIDE.md](ENV_SETUP_GUIDE.md) - Full documentation
- Run `python3 check_env.py` for diagnostics

## What Gets Loaded

| Variable | Required? | Default |
|----------|-----------|---------|
| `ANTHROPIC_API_KEY` | Yes (for AI) | None |
| `DEFAULT_OUTPUT_FOLDER` | No | `~/resume_tailor_output` |

## Verification Commands

```bash
# Interactive check (recommended)
python3 check_env.py

# Quick test
python3 -c "from config.settings import ANTHROPIC_API_KEY; print('✓ Loaded' if ANTHROPIC_API_KEY else '✗ Not loaded')"

# Run tests
python3 -m pytest tests/test_env_loading.py -v
```

## Security Reminder

⚠️ **Never commit your `.env` file to git!**

It's already in `.gitignore`, but be careful not to:
- Share screenshots showing your API key
- Copy/paste your .env file publicly
- Commit it to a public repository

## Need Help?

1. Run `python3 check_env.py` for diagnostics
2. See [ENV_SETUP_GUIDE.md](ENV_SETUP_GUIDE.md) for detailed help
3. Check [README.md](README.md) troubleshooting section
