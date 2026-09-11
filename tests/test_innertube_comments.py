"""Tests for InnerTube comments extraction."""

import pytest

from innertube._comments import CommentsDisabledError, _comments_turned_off, get_comments


def _watch_next(comment_section_contents):
    return {
        "contents": {
            "twoColumnWatchNextResults": {
                "results": {
                    "results": {
                        "contents": [
                            {"videoPrimaryInfoRenderer": {}},
                            {
                                "itemSectionRenderer": {
                                    "sectionIdentifier": "comment-item-section",
                                    "contents": comment_section_contents,
                                }
                            },
                        ]
                    }
                }
            }
        }
    }


def test_comments_turned_off_detects_message_renderer():
    data = _watch_next([{"messageRenderer": {"text": {"runs": [{"text": "Comments are turned off. "}]}}}])
    assert _comments_turned_off(data) is True


def test_comments_turned_off_ignores_continuation():
    data = _watch_next([{"continuationItemRenderer": {"continuationEndpoint": {}}}])
    assert _comments_turned_off(data) is False


def test_comments_turned_off_without_comment_section():
    assert _comments_turned_off({"contents": {}}) is False


@pytest.mark.asyncio
async def test_get_comments_raises_when_turned_off(monkeypatch):
    data = _watch_next([{"messageRenderer": {"text": {"simpleText": "Comments are turned off."}}}])

    async def fake_post(endpoint, body, use_cookies=True):
        return data

    monkeypatch.setattr("innertube._comments.innertube_post", fake_post)
    with pytest.raises(CommentsDisabledError):
        await get_comments("FUfGcZ092b0")


@pytest.mark.asyncio
async def test_get_comments_empty_when_section_missing(monkeypatch):
    async def fake_post(endpoint, body, use_cookies=True):
        return {"contents": {}}

    monkeypatch.setattr("innertube._comments.innertube_post", fake_post)
    result = await get_comments("abc")
    assert result["comments"] == []
