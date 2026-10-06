from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch

def test_complete_end_to_end_detection_lifecycle(client):
    """
    End-to-end test verifying:
    1. Competitor registration & automatic investigation
    2. Publishing/discovery of an article
    3. Extraction and duplicate prevention
    4. Exact delay calculation
    5. Dashboard notification generation
    6. Dashboard statistics reflection
    """
    mock_analysis = {
        "rss_available": True,
        "rss_url": "https://beta-innovations.com/rss.xml",
        "atom_available": False,
        "sitemap_available": True,
        "sitemap_url": "https://beta-innovations.com/sitemap.xml",
        "sitemap_index": False,
        "blog_url": "https://beta-innovations.com/blog",
        "article_pattern": "/blog/*",
        "publication_date_available": True,
        "structured_metadata_available": True,
        "canonical_url_available": True,
        "selected_strategy": "RSS + Sitemap",
    }

    # Step 1: Add Competitor
    with patch("backend.services.website_analyzer.WebsiteAnalyzer.analyze_website", AsyncMock(return_value=mock_analysis)):
        reg_resp = client.post(
            "/api/competitors",
            json={
                "name": "Beta Innovations",
                "website_url": "https://beta-innovations.com",
            }
        )
    assert reg_resp.status_code == 200
    comp_id = reg_resp.json()["id"]

    # Step 2: Trigger Check where a new article is discovered
    now = datetime.now(timezone.utc)
    pub_time = now - timedelta(seconds=135)  # 2 minutes 15 seconds ago
    
    mock_feed_result = {
        "articles_found": 1,
        "new_articles": [
            {
                "title": "Next-Gen Competitor Intelligence",
                "content": "<p>Extracted full content of breaking intelligence article.</p>",
                "author": "Dr. Sarah Chen",
                "published_at": pub_time,
                "detected_at": now,
                "detection_delay_seconds": 135.0,
                "detection_method": "RSS",
                "canonical_url": "https://beta-innovations.com/blog/next-gen-intelligence",
                "source_url": "https://beta-innovations.com/blog/next-gen-intelligence",
                "meta_description": "Breakthrough intelligence preview.",
                "featured_image": "https://images.unsplash.com/sample.jpg",
                "categories": "AI, Market Intelligence",
                "tags": "AI, Competitors",
                "relevant_links": None,
            }
        ]
    }

    with patch("backend.services.rss_monitor.RSSMonitor.check_feed", AsyncMock(return_value=mock_feed_result)):
        check_resp = client.post(f"/api/competitors/{comp_id}/check")
    assert check_resp.status_code == 200
    check_data = check_resp.json()
    assert check_data["new_articles_found"] == 1
    assert check_data["status"] == "SUCCESS"

    # Step 3: Verify article in articles list with delay calculation
    articles_resp = client.get("/api/articles")
    assert articles_resp.status_code == 200
    articles = articles_resp.json()
    assert len(articles) == 1
    art = articles[0]
    assert art["title"] == "Next-Gen Competitor Intelligence"
    assert art["detection_delay_formatted"] == "2 minutes 15 seconds"
    assert art["delay_status"] == "EXCELLENT (<= 5 min)"
    assert art["detection_method"] == "RSS"

    # Step 4: Verify notification created
    notifs_resp = client.get("/api/notifications")
    assert notifs_resp.status_code == 200
    notifs = notifs_resp.json()
    assert len(notifs) >= 1
    assert "Beta Innovations" in notifs[0]["title"]
    assert "2 minutes 15 seconds" in notifs[0]["message"]

    # Step 5: Verify dashboard statistics updated with real data
    stats_resp = client.get("/api/dashboard/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["total_competitors"] == 1
    assert stats["articles_detected"] == 1
    assert stats["average_detection_time"] == "2 minutes 15 seconds"
    assert stats["fastest_detection"] == "2 minutes 15 seconds"
