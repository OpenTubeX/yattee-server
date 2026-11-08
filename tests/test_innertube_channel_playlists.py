"""Regression tests for the current InnerTube channel playlists tab shape."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from innertube._browse import _extract_items_from_continuation, _extract_items_from_tab


def _playlist_lockup(playlist_id, title, count_text):
    return {
        "lockupViewModel": {
            "contentType": "LOCKUP_CONTENT_TYPE_PLAYLIST",
            "contentId": playlist_id,
            "metadata": {"lockupMetadataViewModel": {"title": {"content": title}}},
            "contentImage": {
                "collectionThumbnailViewModel": {
                    "primaryThumbnail": {
                        "thumbnailViewModel": {
                            "image": {"sources": [{"url": "https://i.ytimg.com/vi/x/hqdefault.jpg"}]},
                            "overlays": [
                                {
                                    "thumbnailOverlayBadgeViewModel": {
                                        "thumbnailBadges": [{"thumbnailBadgeViewModel": {"text": count_text}}]
                                    }
                                }
                            ],
                        }
                    }
                }
            },
        }
    }


_CONTINUATION = {
    "continuationItemRenderer": {"continuationEndpoint": {"continuationCommand": {"token": "next-page"}}}
}


def test_playlists_tab_grid_of_lockups():
    """The playlists tab puts playlist lockups in a grid inside an item section."""
    data = {
        "contents": {
            "twoColumnBrowseResultsRenderer": {
                "tabs": [
                    {
                        "tabRenderer": {
                            "content": {
                                "sectionListRenderer": {
                                    "contents": [
                                        {
                                            "itemSectionRenderer": {
                                                "contents": [
                                                    {
                                                        "gridRenderer": {
                                                            "items": [
                                                                _playlist_lockup("PL1", "Vibe Coding", "2 videos"),
                                                                _playlist_lockup("PL2", "Tours", "1,234 videos"),
                                                                _CONTINUATION,
                                                            ]
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

    items, continuation = _extract_items_from_tab(data)

    assert [(item["type"], item["playlistId"], item["videoCount"]) for item in items] == [
        ("playlist", "PL1", 2),
        ("playlist", "PL2", 1234),
    ]
    assert continuation == "next-page"


def test_playlists_tab_continuation_of_lockups():
    data = {
        "onResponseReceivedActions": [
            {
                "appendContinuationItemsAction": {
                    "continuationItems": [_playlist_lockup("PL3", "More", "7 videos"), _CONTINUATION]
                }
            }
        ]
    }

    items, continuation = _extract_items_from_continuation(data)

    assert [(item["playlistId"], item["videoCount"]) for item in items] == [("PL3", 7)]
    assert continuation == "next-page"
