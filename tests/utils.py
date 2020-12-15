from dataclasses import dataclass, field, fields
from typing import Any, Dict, List, Optional

from gidgethub.sansio import Event


def parametrize_id(obj: object) -> str:
    """``Event.delivery_id`` is used as a short description for the respective test
    case and as a way to id the specific test case in the parametrized group."""
    if isinstance(obj, Event):
        return obj.delivery_id
    else:
        return ""


@dataclass(repr=False, eq=False, frozen=True)
class ExpectedData:
    getitem_url: List[str] = field(default_factory=list)
    getiter_url: List[str] = field(default_factory=list)
    post_url: List[str] = field(default_factory=list)
    post_data: List[Dict[str, Any]] = field(default_factory=list)
    patch_url: List[str] = field(default_factory=list)
    patch_data: List[Dict[str, Any]] = field(default_factory=list)
    delete_url: List[str] = field(default_factory=list)
    delete_data: List[Dict[str, Any]] = field(default_factory=list)


class MockGitHubAPI:
    def __init__(
        self,
        *,
        getitem: Optional[Dict[str, Any]] = None,
        getiter: Optional[Dict[str, Any]] = None,
        post: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._getitem_return = getitem
        self._getiter_return = getiter
        self._post_return = post
        self.getitem_url: List[str] = []
        self.getiter_url: List[str] = []
        self.post_url: List[str] = []
        self.post_data: List[Dict[str, Any]] = []
        self.patch_url: List[str] = []
        self.patch_data: List[Dict[str, Any]] = []
        self.delete_url: List[str] = []
        self.delete_data: List[Dict[str, Any]] = []

    @property
    async def access_token(self) -> str:
        return token

    async def getitem(self, url: str, **kwargs: Any) -> Any:
        self.getitem_url.append(url)
        getitem_return = self._getitem_return
        if getitem_return is not None:
            return getitem_return[url]
        else:
            raise AssertionError(
                "Expected to be supplied with the 'getitem' argument when "
                "instantiating the object but got 'None' instead."
            )

    async def getiter(self, url: str, **kwargs: Any) -> Any:
        self.getiter_url.append(url)
        getiter_return = self._getiter_return
        if getiter_return is not None:
            data = getiter_return[url]
        else:
            raise AssertionError(
                "Expected to be supplied with the 'getiter' argument when "
                "instantiating the object but got 'None' instead."
            )
        if isinstance(data, dict) and "items" in data:
            data = data["items"]
        for item in data:
            yield item

    async def post(self, url: str, *, data: Any, **kwargs: Any) -> Any:
        self.post_url.append(url)
        if url == review_url:
            # Comments are arbitrary data, body is a constant and quite long.
            # This is done just for convenience.
            data.pop("body")
            data.pop("comments")
        self.post_data.append(data)
        # XXX Only used for installation. Is it really necessary?
        post_return = self._post_return
        if post_return is not None:
            return post_return[url]

    async def patch(self, url: str, *, data: Any, **kwargs: Any) -> Any:
        self.patch_url.append(url)
        self.patch_data.append(data)

    async def delete(self, url: str, *, data: Any = None, **kwargs: Any) -> None:
        self.delete_url.append(url)
        if data is not None:
            self.delete_data.append(data)

    def __eq__(self, expected: object) -> bool:
        """A small hack to compare directly with the expected data object.

        Get all the fields from the expected data, compare the length and then check
        whether all the data in the expected field value is present in the actual field
        value. By comparing the length first and then checking individual elements,
        we don't have to sort the list. If all the expected values are present in the
        respective actual field, then the data is same in the actual and expected field
        irrespective of the order.
        """
        if not isinstance(expected, ExpectedData):
            return NotImplemented
        for f in fields(expected):
            field_name = f.name
            # Let the ``AttributeError`` propogate, if any.
            actual_value = getattr(self, field_name)
            expected_value = getattr(expected, field_name)
            assert len(actual_value) == len(expected_value), (
                f"Expected the length of '{self.__class__.__name__}.{field_name}' be "
                f"equal to the length of '{expected.__class__.__name__}.{field_name}', "
                f"\n\nActual value: {actual_value}\n\nExpected value: {expected_value}"
            )
            for element in expected_value:
                assert element in actual_value, (
                    f"Expected the element of "
                    f"'{expected.__class__.__name__}.{field_name}' be a member of "
                    f"'{self.__class__.__name__}.{field_name}'\n\nElement: {element}"
                    f"\n\nActual value: {actual_value}\n\n"
                    f"Expected value: {expected_value}"
                )
        return True


# Meta information
token = "12345"
number = 1
repository = "user/testing"
sha = "a06212024d8f1c339c55c5ea4568ech155368c21"
user = "user"
comment = "This is a comment"

# Issue
html_issue_url = f"https://github.com/{repository}/issues/{number}"
issue_path = f"/repos/{repository}/issues"
issue_url = f"https://api.github.com/repos/{repository}/issues/{number}"
labels_url = f"{issue_url}/labels"
comments_url = f"{issue_url}/comments"
comment_url = f"{comments_url}/{number}"
reactions_url = f"{comment_url}/reactions"

# Pull request
pr_url = f"https://api.github.com/repos/{repository}/pulls/{number}"
html_pr_url = f"https://github.com/{repository}/pulls/{number}"
reviewers_url = f"{pr_url}/requested_reviewers"
files_url = f"{pr_url}/files"
contents_url1 = f"https://api.github.com/repos/{repository}/contents/test1.py?ref={sha}"
contents_url2 = f"https://api.github.com/repos/{repository}/contents/test2.py?ref={sha}"
review_url = f"{pr_url}/reviews"

# Check run
check_run_url = f"/repos/{repository}/commits/{sha}/check-runs"

# Search
search_url = (
    f"/search/issues?q=type:pr+state:open+draft:false+repo:{repository}+sha:{sha}"
)
pr_user_search_url = (
    f"/search/issues?q=type:pr+state:open+repo:{repository}+author:{user}"
)

# PR template ticked
CHECKBOX_TICKED = (
    "### **Describe your change:**\n\n\n\n"
    "* [ ] Add an algorithm?\n"
    "* [x] Fix a bug or typo in an existing algorithm?\n"
    "* [x] Documentation change?\n\n"
    "### **Checklist:**\n"
    "* [x] I have read [CONTRIBUTING.md]"
    "(https://github.com/TheAlgorithms/Python/blob/master/CONTRIBUTING.md).\n"
    "* [x] This pull request is all my own work -- I have not plagiarized.\n"
    "* [x] I know that pull requests will not be merged if they fail the automated "
    "tests.\n"
    "* [x] This PR only changes one algorithm file.  To ease review, please open "
    "separate PRs for separate algorithms.\n"
    "* [x] All new Python files are placed inside an existing directory.\n"
    "* [x] All filenames are in all lowercase characters with no spaces or dashes.\n"
    "* [x] All functions and variable names follow Python naming conventions.\n"
    "* [x] All function parameters and return values are annotated with Python "
    "[type hints](https://docs.python.org/3/library/typing.html).\n"
    "* [x] All functions have [doctests]"
    "(https://docs.python.org/3/library/doctest.html) that pass the automated testing."
    "\n"
    "* [x] All new algorithms have a URL in its comments that points to Wikipedia or "
    "other similar explanation.\n"
    "* [ ] If this pull request resolves one or more open issues then the commit "
    "message contains `Fixes: #{$ISSUE_NO}`.\n"
)

# PR template ticked with uppercase 'X'
CHECKBOX_TICKED_UPPER = (
    "### **Describe your change:**\n\n\n\n"
    "* [ ] Add an algorithm?\n"
    "* [X] Fix a bug or typo in an existing algorithm?\n"
    "* [X] Documentation change?\n\n"
    "### **Checklist:**\n"
    "* [X] I have read [CONTRIBUTING.md]"
    "(https://github.com/TheAlgorithms/Python/blob/master/CONTRIBUTING.md).\n"
    "* [X] This pull request is all my own work -- I have not plagiarized.\n"
    "* [X] I know that pull requests will not be merged if they fail the automated "
    "tests.\n"
    "* [X] This PR only changes one algorithm file.  To ease review, please open "
    "separate PRs for separate algorithms.\n"
    "* [X] All new Python files are placed inside an existing directory.\n"
    "* [X] All filenames are in all lowercase characters with no spaces or dashes.\n"
    "* [X] All functions and variable names follow Python naming conventions.\n"
    "* [X] All function parameters and return values are annotated with Python "
    "[type hints](https://docs.python.org/3/library/typing.html).\n"
    "* [X] All functions have [doctests]"
    "(https://docs.python.org/3/library/doctest.html) that pass the automated testing."
    "\n"
    "* [X] All new algorithms have a URL in its comments that points to Wikipedia or "
    "other similar explanation.\n"
    "* [ ] If this pull request resolves one or more open issues then the commit "
    "message contains `Fixes: #{$ISSUE_NO}`.\n"
)

# PR template not ticked
CHECKBOX_NOT_TICKED = (
    "### **Describe your change:**\n\n\n\n"
    "* [ ] Add an algorithm?\n"
    "* [ ] Fix a bug or typo in an existing algorithm?\n"
    "* [ ] Documentation change?\n\n"
    "### **Checklist:**\n"
    "* [ ] I have read [CONTRIBUTING.md]"
    "(https://github.com/TheAlgorithms/Python/blob/master/CONTRIBUTING.md).\n"
    "* [ ] This pull request is all my own work -- I have not plagiarized.\n"
    "* [ ] I know that pull requests will not be merged if they fail the automated "
    "tests.\n"
    "* [ ] This PR only changes one algorithm file.  To ease review, please open "
    "separate PRs for separate algorithms.\n"
    "* [ ] All new Python files are placed inside an existing directory.\n"
    "* [ ] All filenames are in all lowercase characters with no spaces or dashes.\n"
    "* [ ] All functions and variable names follow Python naming conventions.\n"
    "* [ ] All function parameters and return values are annotated with Python "
    "[type hints](https://docs.python.org/3/library/typing.html).\n"
    "* [ ] All functions have [doctests]"
    "(https://docs.python.org/3/library/doctest.html) that pass the automated testing."
    "\n"
    "* [ ] All new algorithms have a URL in its comments that points to Wikipedia or "
    "other similar explanation.\n"
    "* [ ] If this pull request resolves one or more open issues then the commit "
    "message contains `Fixes: #{$ISSUE_NO}`.\n"
)
