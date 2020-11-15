import asyncio
import datetime
import os
from typing import Any

import aiohttp
import cachetools
from aiohttp import web
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing, sansio

from . import check_runs, installations, pull_requests
from .log import Color, logger

router = routing.Router(installations.router, check_runs.router, pull_requests.router)

cache = cachetools.LRUCache(maxsize=500)  # type: cachetools.LRUCache[Any, Any]


async def main(request: web.Request) -> web.Response:
    try:
        body = await request.read()
        secret = os.environ.get("GITHUB_SECRET")
        event = sansio.Event.from_http(request.headers, body, secret=secret)
        if event.event == "ping":
            return web.Response(status=200)
        logger.info(
            "event=%s delivery_id=%s",
            Color.inject(f"{event.event}:{event.data['action']}", "yellow"),
            event.delivery_id,
        )
        async with aiohttp.ClientSession() as session:
            gh = gh_aiohttp.GitHubAPI(
                session, "dhruvmanila/algorithms-keeper", cache=cache
            )
            # Give GitHub some time to reach internal consistency.
            await asyncio.sleep(1)
            await router.dispatch(event, gh)
        try:
            logger.info(
                "ratelimit=%s time_remaining=%s",
                Color.inject(
                    f"{gh.rate_limit.remaining}/{gh.rate_limit.limit}", "yellow"
                ),
                Color.inject(
                    str(
                        gh.rate_limit.reset_datetime
                        - datetime.datetime.now(datetime.timezone.utc)
                    ),
                    "yellow",
                ),
            )
        except AttributeError:
            pass
        return web.Response(status=200)
    except Exception as err:
        logger.exception(err)
        return web.Response(status=500, text=str(err))


if __name__ == "__main__":  # pragma: no cover
    app = web.Application()
    app.router.add_post("/", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)  # type: ignore
    web.run_app(app, port=port)
