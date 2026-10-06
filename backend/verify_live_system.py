import time
import requests
import json

BASE_API = "http://127.0.0.1:8000/api"
DEMO_URL = "http://127.0.0.1:8001"

def print_step(title):
    print(f"\n{'='*70}\n>>> {title}\n{'='*70}")

def verify():
    # 1. System Health Check
    print_step("1. Checking System Status")
    resp = requests.get(f"{BASE_API}/system/status")
    print("System Status:", resp.json())
    assert resp.status_code == 200

    # 2. Add Competitor (Automatic Website Analysis)
    print_step("2. Adding Competitor & Running Automatic Website Analysis")
    comp_payload = {
        "name": "Acme Innovations (Controlled Demo)",
        "website_url": DEMO_URL,
    }
    resp = requests.post(f"{BASE_API}/competitors", json=comp_payload)
    print("Added Competitor Response:", json.dumps(resp.json(), indent=2))
    assert resp.status_code == 200
    comp_data = resp.json()
    comp_id = comp_data["id"]
    strategy = comp_data["selected_strategy"]
    print(f"Discovered Strategy: {strategy}")
    assert "RSS" in strategy or "Sitemap" in strategy

    # Inspect discovered configuration signals
    comp_detail = requests.get(f"{BASE_API}/competitors/{comp_id}").json()
    print("Discovered Configuration Signals:", json.dumps(comp_detail["configuration"], indent=2))
    assert comp_detail["configuration"]["rss_available"] is True
    assert comp_detail["configuration"]["sitemap_available"] is True

    # Allow initial background registration scan to settle
    time.sleep(2)

    # 3. Publish a Brand New Article on the Demo Website
    print_step("3. Publishing Brand New Test Article on Demo Website")
    pub_resp = requests.post(f"{DEMO_URL}/api/publish", json={"title": "Exclusive: Quantum AI Processing Breakthrough"})
    print("Demo Publish Output:", pub_resp.json())
    assert pub_resp.status_code == 200
    time.sleep(2)  # Wait 2 seconds to generate a realistic detection delay

    # 4. Trigger Detection Check
    print_step("4. Triggering Detection Check on Competitor")
    check_resp = requests.post(f"{BASE_API}/competitors/{comp_id}/check")
    print("Check Response:", json.dumps(check_resp.json(), indent=2))
    assert check_resp.status_code == 200
    check_data = check_resp.json()
    assert check_data["status"] == "SUCCESS"
    assert check_data["new_articles_found"] >= 1

    # 5. Verify Article Extraction and Exact Detection Delay
    print_step("5. Verifying Article Extraction, Delay Calculation, and Delay Status")
    articles_resp = requests.get(f"{BASE_API}/articles?competitor_id={comp_id}")
    articles = articles_resp.json()
    print(f"Total Ingested Articles: {len(articles)}")
    newest = articles[0]
    print(f"Article Title: {newest['title']}")
    print(f"Detection Method: {newest['detection_method']}")
    print(f"Publication Date: {newest['published_at']}")
    print(f"Detection Date: {newest['detected_at']}")
    print(f"Exact Detection Delay (seconds): {newest['detection_delay_seconds']}")
    print(f"Exact Detection Delay Formatted: {newest['detection_delay_formatted']}")
    print(f"Performance Status: {newest['delay_status']}")
    assert newest["detection_delay_seconds"] is not None
    assert "second" in newest["detection_delay_formatted"] or "minute" in newest["detection_delay_formatted"]

    # 6. Verify Duplicate Prevention
    print_step("6. Verifying Duplicate Prevention by Running Check Again")
    check2_resp = requests.post(f"{BASE_API}/competitors/{comp_id}/check")
    check2_data = check2_resp.json()
    print("Second Check Response:", json.dumps(check2_data, indent=2))
    assert check2_data["new_articles_found"] == 0, "Duplicate article was unexpectedly added!"
    print("Duplicate prevention verified: 0 new articles added on repeat check.")

    # 7. Verify Dashboard Notifications
    print_step("7. Verifying Real-Time Dashboard Notification")
    notif_resp = requests.get(f"{BASE_API}/notifications")
    notifs = notif_resp.json()
    print("Latest Notification:", json.dumps(notifs[0], indent=2))
    assert len(notifs) >= 1
    assert "Acme Innovations" in notifs[0]["title"]

    # 8. Error Isolation: Simulate a Failed Website
    print_step("8. Simulating Failed Website & Testing Error Isolation")
    fail_comp_payload = {
        "name": "Unreachable Competitor",
        "website_url": "http://127.0.0.1:9999/broken",
        "rss_url": "http://127.0.0.1:9999/feed.xml",
    }
    fail_comp = requests.post(f"{BASE_API}/competitors", json=fail_comp_payload).json()
    fail_id = fail_comp["id"]
    
    # Trigger check on the broken competitor
    fail_check = requests.post(f"{BASE_API}/competitors/{fail_id}/check").json()
    print("Failed Site Check Result:", json.dumps(fail_check, indent=2))
    assert fail_check["status"] == "FAILED"

    # Verify that the primary competitor check STILL works perfectly!
    healthy_check = requests.post(f"{BASE_API}/competitors/{comp_id}/check").json()
    print("Healthy Site Check Result After Failure:", json.dumps(healthy_check, indent=2))
    assert healthy_check["status"] == "SUCCESS"
    print("Error isolation verified: Failed competitor did not impede healthy site monitoring.")

    # 9. Concurrency & 100-Website Scale Benchmark
    print_step("9. Running 100-Website Concurrency Benchmark")
    scale_start = requests.post(f"{BASE_API}/scale-test/start", json={"total_targets": 100, "concurrent_workers": 15}).json()
    print("Scale Test Started:", scale_start)
    time.sleep(3)
    scale_status = requests.get(f"{BASE_API}/scale-test/status").json()
    print("Scale Test Metrics Snapshot:")
    print(f"  Total Targets: {scale_status['total_targets']}")
    print(f"  Active Workers: {scale_status['active_workers']}")
    print(f"  Completed: {scale_status['completed_tasks']}")
    print(f"  Failures Isolated: {scale_status['failed_tasks']}")
    print(f"  Avg Latency: {scale_status['avg_response_time_ms']} ms")
    print(f"  Throughput: {scale_status['throughput_checks_per_sec']} checks/sec")
    assert scale_status["completed_tasks"] > 0

    # 10. Dashboard Stats
    print_step("10. Fetching Dashboard Stats")
    stats = requests.get(f"{BASE_API}/dashboard/stats").json()
    print("Dashboard Stats:", json.dumps(stats, indent=2))
    assert stats["total_competitors"] >= 2
    assert stats["articles_detected"] >= 1
    assert stats["failed_checks"] >= 1
    assert stats["average_detection_time"] is not None

    print("\n" + "="*70)
    print("ALL 10 LIVE SYSTEM CAPABILITIES VERIFIED WITH 100% SUCCESS!")
    print("="*70)

if __name__ == "__main__":
    verify()
