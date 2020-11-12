from typing import Any

from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing, sansio

from . import utils
from .constants import Label
from .logging import logger

router = routing.Router()


@router.register("check_run", action="completed")
async def check_ci_status_and_label(
    event: sansio.Event,
    gh: gh_aiohttp.GitHubAPI,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Add and remove label when any of the check runs fail.

    This event will be triggered on every check run when it is completed but we only
    want to know the final conclusion. So, the `if` statement makes sure we execute
    the block only when the last check run is completed.
    """
    installation_id = event.data["installation"]["id"]
    repository = event.data["repository"]["full_name"]

    try:
        commit_sha = event.data["check_run"]["head_sha"]
        pr_for_commit = await utils.get_pr_for_commit(
            gh, installation_id, sha=commit_sha, repository=repository
        )
    except KeyError:
        # This event is routed from the pull_requests module and is triggered when a
        # PR is made ready for review.
        commit_sha = event.data["pull_request"]["head"]["sha"]
        pr_for_commit = event.data["pull_request"]

    # The log message is a bit ambiguous as there are multiple possibilities for
    # `pr_for_commit` to be `None`:
    # - PR could have been closed before all the checks were completed as
    #   the bot might have found it invalid.
    # - PR could be in draft mode
    # - CheckRun event came from a commit made directly on master branch
    if pr_for_commit is None:
        logger.info(
            "Pull request not found for commit: https://github.com/%s/commit/%s",
            repository,
            commit_sha,
        )
        return None

    check_runs = await utils.get_check_runs_for_commit(
        gh, installation_id, sha=commit_sha, repository=repository
    )

    all_check_run_status = [
        check_run["status"] for check_run in check_runs["check_runs"]
    ]
    all_check_run_conclusion = [
        check_run["conclusion"] for check_run in check_runs["check_runs"]
    ]

    if (
        "in_progress" not in all_check_run_status
        and "queued" not in all_check_run_status
    ):  # wait until all check runs are completed
        pr_labels = [label["name"] for label in pr_for_commit["labels"]]
        if any(
            element in [None, "failure", "timed_out"]
            for element in all_check_run_conclusion
        ):  # Add the failure label only if it doesn't exist
            if Label.FAILED_TEST not in pr_labels:
                await utils.add_label_to_pr_or_issue(
                    gh,
                    installation_id,
                    label=Label.FAILED_TEST,
                    pr_or_issue=pr_for_commit,
                )
        # Check run is successful so if the label exist, remove it
        elif Label.FAILED_TEST in pr_labels:
            await utils.remove_label_from_pr_or_issue(
                gh,
                installation_id,
                label=Label.FAILED_TEST,
                pr_or_issue=pr_for_commit,
            )
