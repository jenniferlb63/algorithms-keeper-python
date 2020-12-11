"""Package level constants

Only the constants which are accessed throughout the module are defined here.
Constants related to a specific event are defined in their own module. So a
constant related to pull request will be defined in the `pull_requests` module.
"""


class Label:
    FAILED_TEST = "Status: Tests are failing"
    AWAITING_REVIEW = "Status: awaiting reviews"
    ANNOTATIONS = "Require: Type hints"
    REQUIRE_TEST = "Require: Tests"
    DESCRIPTIVE_NAMES = "Require: Descriptive names"
    CHANGES_REQUESTED = "Status: awaiting changes"
    INVALID = "invalid"
    DOCUMENTATION = "Type: documentation"
    ENHANCEMENT = "Type: enhancement"


class Missing:
    TYPE_HINT = "type hint"
    DOCTEST = "doctest"
    RETURN_TYPE_HINT = "return type hint"
    DESCRIPTIVE_NAME = "descriptive name"


# Mapping of missing requirement to the appropriate label.
# ``Missing.RETURN_TYPE_HINT`` and ``Missing.TYPE_HINT`` corresponds to the same label.
REQUIREMENT_TO_LABEL = {
    Missing.DOCTEST: Label.REQUIRE_TEST,
    Missing.TYPE_HINT: Label.ANNOTATIONS,
    Missing.DESCRIPTIVE_NAME: Label.DESCRIPTIVE_NAMES,
}

# If these labels are on a pull request, then the pull request is not ready to be
# reviewed by a maintainer and thus, remove Label.AWAITING_REVIEW if present.
PR_NOT_READY_LABELS = (
    Label.FAILED_TEST,
    Label.REQUIRE_TEST,
    Label.DESCRIPTIVE_NAMES,
    Label.ANNOTATIONS,
    Label.INVALID,
)


# All the comments made by the bot

GREETING_COMMENT = """\
This is the algorithms-keeper at your service! Thank you for installing me @{login}.
"""

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

EMPTY_ISSUE_BODY_COMMENT = """\
# Closing this issue as invalid

@{user_login}, this issue is being closed because the description is empty. \
If you believe that this is being done by mistake, please open the issue with the \
necessary details regarding the problem.
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

INVALID_EXTENSION_COMMENT = """\
# Closing this pull request as invalid

@{user_login}, this pull request is being closed as the files submitted contains an \
invalid extension. This repository only accepts Python algorithms. Please read the \
[Contributing guidelines]\
(https://github.com/TheAlgorithms/Python/blob/master/CONTRIBUTING.md) first.

Invalid files in this pull request: `{files}`
"""

PR_REVIEW_BODY = """\
<details>
<summary><b><em>Click here to look at the relevant links :arrow_down:</em></b></summary>
<br>
<blockquote>

## :link: Relevant Links
### Repository:
- [Contributing guidelines]\
(https://github.com/TheAlgorithms/Python/blob/master/CONTRIBUTING.md)
- [Project Euler solution guidelines]\
(https://github.com/TheAlgorithms/Python/blob/master/project_euler/README.md)
### Python:
- [Type hints](https://docs.python.org/3/library/typing.html)
- [`doctest`](https://docs.python.org/3/library/doctest.html)
- [`unittest`](https://docs.python.org/3/library/unittest.html)
- [`pytest`](https://docs.pytest.org/en/stable/)

</blockquote>
</details>

###### Automated review generated by [algorithms-keeper]\
(https://github.com/dhruvmanila/algorithms-keeper). If there's any problem regarding \
this review, [please open an issue about it.]\
(https://github.com/dhruvmanila/algorithms-keeper/issues)

---
<details>
<summary><code>algorithms-keeper</code> commands and options</summary>
<br>
<blockquote>

### algorithms-keeper actions can be triggered by commenting on this PR:
- `@algorithms-keeper review` to trigger the checks for only added pull request files
- `@algorithms-keeper review-all` to trigger the checks for all the pull request \
files, including the modified files. As we cannot post review comments on lines not \
part of the diff, this command will only modify the labels accordingly.

NOTE: Commands are in beta and so this feature is restricted only to a member or owner \
of the organization.
</blockquote>
"""
