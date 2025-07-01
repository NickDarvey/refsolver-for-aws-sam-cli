# Work

## 1. [ ] Make AWS SAM user-friendly

So far we've got neat library functions which can be composed together. However, our users just want to use SAM CLI.
That is, we want them to be able to call `sam local invoke MyFunction --env-vars MyFunction.env.json --profile sandbox` using an `.env.json` we have generated for them where we've resolved any refs.
Note:

1. We should not wrap calls (to SAM CLI or CDK CLI) but keep writing things in a composable manner.
2. Users will probably include this function call in a pyinvoke task, so make it neat to use from Python.

## 2. [ ] Turn this into a nice tool to call from terminal

Some users might want to use it from the terminal, so we should make a function which is ergonomic to use there.
Note:

1. It should the assembly dir and function name from args, create a default session, and write the output env var JSON (defaulting to use the function name).
2. Update the Python project so it will make something executable available when installed, ideally like `refsolver ...`.
3. Prefer explicitly named args over positional.

## 3. [ ] Rewrite the usage section of the README

1. Update the README usage section to focus on the CLI usage and two high-level function usage.

## 4. [ ] Implement a build pipeline

1. We are using GitHub so use GitHub actions.
2. Every commit to main or every commit on an open PR should run the pipeline.
3. The pipeline should check formatting and linting and fail if there are any issues.
4. The pipeline should run _unit_ tests and report results so they are shown nicely in GitHub. (We won't try to add integration tests to the pipeline yet.)
5. The pipeline should get code coverage eval and report results so they are shown nicely in GitHub.
6. PR flow
   - We'll use trunk-based development.
   - PRs should only be allowed to merge to main when 3, 4, and 5 have passed.
   - No one should be allowed to commit to main except via PR.
   - Merges to main should be squashed.

## 5. [ ] Implement a release pipeline

1. We want to use trunk-based development where every commit on main produces a new version of the package.
2. We'll eventually publish this to PyPI, but for starters, let's just publish it as a release in GitHub.
3. Each commit to main should increment the version number of the release. There may be some semver tooling we can use so this we can bump major/minor via commit messages.
