# GitHub release checklist

Before publishing:

1. Edit `README.md` and replace `YOUR_ORG` with your GitHub org/user.
2. Edit `.codex-plugin/plugin.json` and replace `YOUR_ORG` plus display metadata.
3. Decide whether MIT is the correct license for your use case.
4. Run:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
paper-hs --help
```

5. Create a smoke project:

```bash
paper-hs init --project ./workspace/smoke --title "Smoke" --venue "test" --source examples/minimal_latex --install-skill
paper-hs source-cards --project ./workspace/smoke
paper-hs verify --project ./workspace/smoke
```

6. Commit:

```bash
git init
git add .
git commit -m "Initial Paper-HS release"
```

7. Push to GitHub.
