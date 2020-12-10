# algorithms-keeper
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/dhruvmanila/algorithms-keeper/CI?label=CI&logo=github&style=flat-square)](https://github.com/dhruvmanila/algorithms-keeper/actions)
[![Codecov](https://img.shields.io/codecov/c/gh/dhruvmanila/algorithms-keeper?label=codecov&logo=codecov&style=flat-square)](https://codecov.io/gh/dhruvmanila/algorithms-keeper)
[![code style: black](https://img.shields.io/static/v1?label=code%20style&message=black&color=black&style=flat-square)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/static/v1?label=mypy&message=checked&style=flat-square&color=2a6db2&labelColor=505050)](http://mypy-lang.org/)

A bot for [TheAlgorithms/Python](https://www.github.com/TheAlgorithms/Python) repository. This bot is based on [this tutorial](https://github-app-tutorial.readthedocs.io/en/latest/index.html) and also inspired by the ones working for the [CPython](https://github.com/python/cpython) repository which are [miss-islington](https://github.com/python/miss-islington), [bedevere](https://github.com/python/bedevere) and [the-knights-who-say-ni](https://github.com/python/the-knights-who-say-ni). This bot is basically a GitHub app which can be installed in any repository using [this link](https://github.com/apps/algorithms-keeper).

***NOTE: This bot is highly configured for [TheAlgorithms/Python](https://www.github.com/TheAlgorithms/Python) repository. DO NOT INSTALL the bot without reading what it actually does.***

## What the bot does:

### Greet the user for installing the app
Open an issue with the message greeting the user who either installed the app or added a new repository to the installed app and then close the issue.

### Add or remove label(s) to pull requests
- To indicate that some of the tests are failing for this pull request if it is not present and remove it when all the tests are passing. It does nothing if the tests are already passing. ***NOTE: This check will be skipped if the pull request is in draft mode.***
- To indicate that the pull request is ready to be reviewed by a maintainer which means all the checks are passing and all the requirements have been satisfied.
- To indicate the user that a maintainer has requested some changes to their submission.

The pull request label stages can be best described in a [graphviz](http://www.webgraphviz.com/) diagram whose code is in the [pull requests module](https://github.com/dhruvmanila/algorithms-keeper/blob/master/algorithms_keeper/pull_requests.py).

### Close invalid pull requests
A pull request is considered invalid if:
- It doesn't contain any description.
- The user has not ticked any of the checkboxes in the provided pull request template.
- The file extension is invalid. For now only PRs with extensionless files are closed.

***NOTE: These checks will be skipped for any member or owner of the organization and also for the pull request which is in draft mode.***

### Close additional pull requests by user
A user will be allowed a fix number of pull requests at a time which will be indicated by the `MAX_PR_BY_USER` constant. This is done so as to avoid spam pull requests. This can be disabled by updating the constant value to 0: `MAX_PR_BY_USER = 0`.

***NOTE: These checks will be skipped for any member or owner of the organization and also for the pull request which is in draft mode.***

### Check all Python files in a pull request
All the Python files will be checked for tests [`doctest`/`unittest`/`pytest`], type hints and descriptive class/function/parameter names. Labels will be added and/or removed according to the latest commit in a pull request. The bot will post the review with all the details regarding the missing requirements.

***NOTE: These checks will be skipped if the pull request is in draft mode and if the pull request is invalid.***

### Commands
Some of the actions of the bot can be triggered using commands:
- `@algorithms-keeper review` to trigger the checks for all the pull request files. ***This command is valid only if it is commented on a pull request and only by either a member or owner of the organization.***

## Logging
There are three loggers out of which one is the main `logger` for the bot that is being used to log certain events and exceptions. The other two loggers are: `aiohttp.access` from `aiohttp.log.access_logger`, used to log `POST` requests made by GitHub for delivering the payload and `api`, used to log all the API calls made to GitHub. The logs can be viewed best using the following command ([_requires Heroku CLI_](https://devcenter.heroku.com/articles/heroku-cli#download-and-install)):
```commandline
heroku logs -a algorithms-keeper -d web -t
```
