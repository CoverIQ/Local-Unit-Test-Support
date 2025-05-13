# Contributing
## Branching Strategy
- main – stable production-ready code
- dev – development integration branch
- feature/xxx new features that are in progress

## How to Contribute
1. Create a new branch from dev:
```bash
git checkout dev
git pull
git checkout -b feature/my-feature
```

2. Commit and push your changes:
```bash
git add .
git commit -m "Add my feature"
git push origin feature/my-feature
```

3. Regularly pull from dev if you want to stay updated and reduce merge conflicts.
```bash
git checkout feature/my-feature
git pull origin dev
```

4. If you want to merge to dev, open a Pull Request to merge.

5. Notify other members to review and approve your pull request.

## Run the Regression Test feature
```bash
# python RegressionTest/main.py source_path tests_path
python RegressionTest/main.py . ./tests/
```