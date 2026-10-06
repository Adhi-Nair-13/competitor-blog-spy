from unittest.mock import AsyncMock, patch

def test_competitor_creation_and_listing(client):
    # Mock analyzer so we don't make outbound network requests during quick tests
    mock_analysis = {
        "rss_available": True,
        "rss_url": "https://company-alpha.com/rss.xml",
        "atom_available": False,
        "sitemap_available": True,
        "sitemap_url": "https://company-alpha.com/sitemap.xml",
        "sitemap_index": False,
        "blog_url": "https://company-alpha.com/blog",
        "article_pattern": "/blog/*",
        "publication_date_available": True,
        "structured_metadata_available": True,
        "canonical_url_available": True,
        "selected_strategy": "RSS + Sitemap",
    }

    with patch("backend.services.website_analyzer.WebsiteAnalyzer.analyze_website", AsyncMock(return_value=mock_analysis)):
        response = client.post(
            "/api/competitors",
            json={
                "name": "Company Alpha",
                "website_url": "https://company-alpha.com",
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Company Alpha"
    assert data["selected_strategy"] == "RSS + Sitemap"
    comp_id = data["id"]

    # Test list endpoint
    list_resp = client.get("/api/competitors")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # Test get competitor detail
    detail_resp = client.get(f"/api/competitors/{comp_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["competitor"]["name"] == "Company Alpha"
    assert detail_data["configuration"]["rss_available"] is True

def test_dashboard_stats_endpoint(client):
    resp = client.get("/api/dashboard/stats")
    assert resp.status_code == 200
    stats = resp.json()
    assert "total_competitors" in stats
    assert "active_competitors" in stats
    assert "articles_detected" in stats
    assert "average_detection_time" in stats

def test_scale_test_endpoint(client):
    start_resp = client.post("/api/scale-test/start", json={"total_targets": 10, "concurrent_workers": 2})
    assert start_resp.status_code == 200

    status_resp = client.get("/api/scale-test/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert "total_targets" in status_data
    assert "avg_response_time_ms" in status_data
