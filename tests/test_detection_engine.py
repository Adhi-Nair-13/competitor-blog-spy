import pytest
from unittest.mock import AsyncMock, patch
from backend.models.competitor import Competitor
from backend.models.article import Article
from backend.models.monitoring_check import MonitoringCheck
from backend.services.detection_engine import DetectionEngine

@pytest.mark.asyncio
async def test_duplicate_prevention(db_session):
    competitor = Competitor(
        name="Test Corp",
        website_url="https://testcorp.com",
        rss_url="https://testcorp.com/feed",
        selected_strategy="RSS",
        monitoring_enabled=True,
    )
    db_session.add(competitor)
    db_session.commit()

    engine = DetectionEngine(db_session)

    mock_article_payload = {
        "articles_found": 1,
        "new_articles": [
            {
                "title": "Unique Article 1",
                "content": "Article Content",
                "author": "Alice",
                "published_at": None,
                "detection_delay_seconds": None,
                "detection_method": "RSS",
                "canonical_url": "https://testcorp.com/blog/unique-1",
                "source_url": "https://testcorp.com/blog/unique-1",
            }
        ]
    }

    # First check: article is newly added
    with patch.object(engine.rss_monitor, "check_feed", AsyncMock(return_value=mock_article_payload)):
        check1 = await engine.run_check_for_competitor(competitor.id)

    assert check1.new_articles_found == 1
    articles_count_1 = db_session.query(Article).count()
    assert articles_count_1 == 1

    # Second check with same article returned: duplicate must be prevented!
    with patch.object(engine.rss_monitor, "check_feed", AsyncMock(return_value=mock_article_payload)):
        check2 = await engine.run_check_for_competitor(competitor.id)

    assert check2.new_articles_found == 0
    articles_count_2 = db_session.query(Article).count()
    assert articles_count_2 == 1  # Still 1, no duplicate created!

@pytest.mark.asyncio
async def test_failed_website_handling_without_stopping_system(db_session):
    competitor = Competitor(
        name="Broken Site",
        website_url="https://brokensite.xyz",
        rss_url="https://brokensite.xyz/feed",
        selected_strategy="RSS",
        monitoring_enabled=True,
    )
    db_session.add(competitor)
    db_session.commit()

    engine = DetectionEngine(db_session)

    # Simulate network timeout / connection refused
    with patch.object(engine.rss_monitor, "check_feed", AsyncMock(side_effect=Exception("Connection refused / DNS failure"))):
        check = await engine.run_check_for_competitor(competitor.id)

    # Check must be recorded as FAILED without unhandled crash
    assert check.status == "FAILED"
    assert "Connection refused" in check.error_message
    assert competitor.monitoring_status == "ERROR"
