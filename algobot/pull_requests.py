import re
from pathlib import PurePath
from typing import Any

from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing, sansio

from . import utils
from .parser import PullRequestFilesParser

MAX_PR_PER_USER = 1

MAX_PR_REACHED_COMMENT = """\
# Multiple Pull Request Detected

@{user_login}, we are extremely excited that you want to submit multiple algorithms \
in this repository but we have a limit on how many pull request a user can keep open \
at a time. This is to make sure all maintainers and users focus on a limited number of \
pull requests at a time to maintain the quality of the code.

This pull request is being closed as the user already has an open pull request. \
Please focus on your previous pull request before opening another one. Thank you for \
your cooperation.

User opened pull requests (including this one): {pr_number}
"""

EMPTY_BODY_COMMENT = """\
# Closing this pull request as invalid

@{user_login}, this pull request is being closed because the description is empty. \
If you believe that this is being done by mistake, please read our \
[Contributing guidelines]\
(https://github.com/TheAlgorithms/Python/blob/master/CONTRIBUTING.md) before opening \
a new pull request with our [template]\
(https://github.com/TheAlgorithms/Python/blob/master/.github/pull_request_template.md) \
properly filled out. Thank you for your interest in our project.
"""

CHECKBOX_NOT_TICKED_COMMENT = """\
# Closing this pull request as invalid

@{user_login}, this pull request is being closed as none of the checkboxes have been \
marked. It is important that you go through the checklist and mark the ones relevant \
to this pull request. Please read the [Contributing guidelines]\
(https://github.com/TheAlgorithms/Python/blob/master/CONTRIBUTING.md).

If you're facing any problem on how to mark a checkbox, please read the following \
instructions:
- Read a point one at a time and think if it is relevant to the pull request or not.
- If it is, then mark it by putting a `x` between the square bracket like so: `[x]`

***NOTE: Only `[x]` is supported so if you have put any other letter or symbol \
between the brackets, that will be marked as invalid. If that is the case then please \
open a new pull request with the appropriate changes.***
"""

NO_EXTENSION_COMMENT = """\
# Closing this pull request as invalid

@{user_login}, this pull request is being closed as the files submitted contains no \
extension. This repository only accepts Python algorithms. Please read the \
[Contributing guidelines]\
(https://github.com/TheAlgorithms/Python/blob/master/CONTRIBUTING.md) first.
"""

PR_REPORT_COMMENT = """\
# Pull Request Report

@{user_login} Hello! I'm a bot made to check all the pull request Python files. \
First of all, I want to say thank you for your time and interest in this project and \
for opening a pull request.

I have detected errors in some of the Python files submitted in this pull request. \
Please read through the report and make the necessary changes. You can take a look at \
the relevant links provided after the report.

### What are node paths?
The report contain headings and a checklist where the items are paths to the \
class/function/parameter where the error is present. Node paths are double colon `::` \
separated names and can be any of the following format:
- Class path: `[file_name]::[class_name]`
- Function path: `[file_name]::[function_name]`
- Function parameter path: `[file_name]::[function_name]::[parameter_name]`
- Method path: `[file_name]::[class_name]::[function_name]`
- Method parameter path: `[file_name]::[class_name]::[function_name]::[parameter_name]`
{content}

### Relevant links:

- Contributing guidelines: \
https://github.com/TheAlgorithms/Python/blob/master/CONTRIBUTING.md
- Project Euler solution guidelines: \
https://github.com/TheAlgorithms/Python/blob/master/project_euler/README.md
- Type hints: https://docs.python.org/3/library/typing.html
- `doctest`: https://docs.python.org/3/library/doctest.html
- `unittest`: https://docs.python.org/3/library/unittest.html
- `pytest`: https://docs.pytest.org/en/stable/
"""

router = routing.Router()


@router.register("pull_request", action="opened")
async def close_invalid_or_additional_pr(
    event: sansio.Event,
    gh: gh_aiohttp.GitHubAPI,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Close an invalid pull request or close additional pull requests made by the
    user and dismiss all the review requests from it.

    A pull request is considered invalid if:
    - It doesn't contain any description
    - The user has not ticked any of the checkboxes in the pull request template
    - The file extension is invalid (Extensionless files) [This will be checked in
      `check_pr_files` function]

    A user will be allowed a fix number of pull requests at a time which will be
    indicated by the `MAX_PR_BY_USER` constant. This is done so as to avoid spam PRs.
    To disable the limit -> `MAX_PR_BY_USER` = 0

    These checks won't be done for the pull request made by a member or owner of the
    organization.
    """
    installation_id = event.data["installation"]["id"]
    pull_request = event.data["pull_request"]
    author_association = pull_request["author_association"].lower()

    if author_association in {"owner", "member"}:
        print(
            f"[SKIPPED] Author association {author_association!r}: "
            f"{pull_request['html_url']}"
        )
        return None

    pr_body = pull_request["body"]
    pr_author = pull_request["user"]["login"]
    comment = None

    if not pr_body:
        comment = EMPTY_BODY_COMMENT.format(user_login=pr_author)
        print(f"[DETECTED] Empty body: {pull_request['html_url']}")
    elif not re.search(r"\[x]", pr_body):
        comment = CHECKBOX_NOT_TICKED_COMMENT.format(user_login=pr_author)
        print(f"[DETECTED] Empty checklist: {pull_request['html_url']}")

    if comment:
        await utils.close_pr_or_issue(
            gh,
            installation_id,
            comment=comment,
            pr_or_issue=pull_request,
            label="invalid",
        )
    elif MAX_PR_PER_USER > 0:
        user_pr_numbers = await utils.get_total_open_prs(
            gh,
            installation_id,
            repository=event.data["repository"]["full_name"],
            user_login=pr_author,
            count=False,
        )

        if len(user_pr_numbers) > MAX_PR_PER_USER:
            print(f"[DETECTED] Multiple open pull requests: {pull_request['html_url']}")
            # Convert list of numbers to: "#1, #2, #3"
            pr_number = "#{}".format(", #".join(map(str, user_pr_numbers)))
            await utils.close_pr_or_issue(
                gh,
                installation_id,
                comment=MAX_PR_REACHED_COMMENT.format(
                    user_login=pr_author, pr_number=pr_number
                ),
                pr_or_issue=pull_request,
            )


@router.register("pull_request", action="opened")
@router.register("pull_request", action="synchronize")
async def check_pr_files(
    event: sansio.Event,
    gh: gh_aiohttp.GitHubAPI,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Check all the pull request files for extension, type hints, tests and
    class, function and parameter names.

    This function will accomplish the following tasks:
    - Check for file extension and close the pull request if a file do not contain any
      extension. Ignores all non-python files and any file in `.github` directory.
    - Check for type hints, tests and descriptive names in the submitted files and
      label it appropriately. Sends the report if there are any errors only when the
      pull request is opened.

    This function will also be triggered when new commits are pushed to the opened pull
    request.
    """
    installation_id = event.data["installation"]["id"]
    pull_request = event.data["pull_request"]

    pr_labels = [label["name"] for label in pull_request["labels"]]
    pr_author = pull_request["user"]["login"]
    pr_files = await utils.get_pr_files(gh, installation_id, pull_request=pull_request)
    parser = PullRequestFilesParser()
    files_to_check = []

    # We will collect all the files first as there is this one problem case:
    # A pull request with two files: `main.py` and `test_main.py`
    # If in this loop, the main file came first, we will check for `doctest` even though
    # there is a separate test file. We cannot hope that the test file comes first in
    # the loop.
    for file in pr_files:
        filepath = PurePath(file["filename"])
        if not filepath.suffix and ".github" not in filepath.parts:
            await utils.close_pr_or_issue(
                gh,
                installation_id,
                comment=NO_EXTENSION_COMMENT.format(user_login=pr_author),
                pr_or_issue=pull_request,
                label="invalid",
            )
            return None
        elif filepath.suffix != ".py" or filepath.name.startswith("__"):
            continue
        # If there is a test file then we do not want to check for `doctest`.
        # NOTE: This should come after the check for `.py` files.
        elif filepath.name.startswith("test_") or filepath.name.endswith("_test.py"):
            parser.skip_doctest = True
        files_to_check.append(file)

    for file in files_to_check:
        code = await utils.get_file_content(gh, installation_id, file=file)
        parser.parse_code(file["filename"], code)

    labels_to_add, labels_to_remove = parser.labels_to_add_and_remove(pr_labels)

    if labels_to_add:
        await utils.add_label_to_pr_or_issue(
            gh, installation_id, label=labels_to_add, pr_or_issue=pull_request
        )

    if labels_to_remove:
        await utils.remove_label_from_pr_or_issue(
            gh, installation_id, label=labels_to_remove, pr_or_issue=pull_request
        )

    # Comment the report data only when the pull request is opened and if there are
    # any errors
    if event.data["action"] == "opened":
        report_content = parser.create_report_content()
        if report_content:
            print(
                f"[DETECTED] Missing requirements in parsed files ({files_to_check}): "
                f"{pull_request['html_url']}"
            )
            await utils.add_comment_to_pr_or_issue(
                gh,
                installation_id,
                comment=PR_REPORT_COMMENT.format(
                    content=report_content, user_login=pr_author
                ),
                pr_or_issue=pull_request,
            )
