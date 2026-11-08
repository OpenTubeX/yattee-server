"""Regression tests for videos that InnerTube search nests in topic shelves."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from innertube._search import _parse_search_results


def _video(video_id):
    return {"videoRenderer": {"videoId": video_id, "title": {"runs": [{"text": video_id}]}}}


def _grid_video(video_id):
    return {
        "gridVideoRenderer": {
            "videoId": video_id,
            "title": {"simpleText": video_id},
            "shortBylineText": {
                "runs": [{"text": "Doopa", "navigationEndpoint": {"browseEndpoint": {"browseId": "UCdoopa"}}}]
            },
        }
    }


def _sections(contents):
    return {
        "contents": {
            "twoColumnSearchResultsRenderer": {
                "primaryContents": {"sectionListRenderer": {"contents": [{"itemSectionRenderer": {"contents": contents}}]}}
            }
        }
    }


def test_topic_shelf_videos_are_results():
    data = _sections(
        [
            _video("a"),
            {
                "shelfRenderer": {
                    "title": {"simpleText": "Minecraft server join"},
                    "content": {"horizontalListRenderer": {"items": [_grid_video("b"), _grid_video("a")]}},
                }
            },
            {"shelfRenderer": {"content": {"verticalListRenderer": {"items": [_video("c")]}}}},
            # Shorts shelves only name the videos, without their channels
            {"gridShelfViewModel": {"contents": [{"shortsLockupViewModel": {"entityId": "shorts-shelf-item-d"}}]}},
        ]
    )

    results, _ = _parse_search_results(data)

    assert [item["videoId"] for item in results] == ["a", "b", "c"]
    assert results[1]["author"] == "Doopa"
    assert results[1]["authorId"] == "UCdoopa"
