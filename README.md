# Competitor Blog Spy & Real-Time Content Monitoring System

A production-grade, full-stack intelligence platform that continuously monitors competitor websites, discovers monitoring sources automatically (RSS/Atom, XML Sitemaps, and Direct Page DOM diffing), detects newly published articles in real-time, calculates exact detection delay down to the second against a 5-minute performance SLA, prevents duplicates, isolates website failures, and scales concurrently to 100+ websites.

Built with **FastAPI**, **React (Vite + Tailwind CSS)**, **SQLAlchemy**, **APScheduler**, and **Recharts**.

---

## Architecture Overview

```
                                  +-----------------------------+
                                  |    React + Vite Frontend    |
                                  | (Dashboard, Alerts, Charts) |
                                  +--------------+--------------+
                                                 | REST API
                                                 v
+------------------------------------------------+-----------------------------------------------+
|                                      FastAPI Backend Engine                                     |
|                                                                                                |
|   +-----------------------+     +------------------------+     +---------------------------+   |
|   |   Website Analyzer    |     |   Detection Engine     |     |   Continuous Scheduler    |   |
|   | (RSS/Sitemap/DOM Scan)|     | (Multi-strategy Runner)|     |  (APScheduler + Workers)  |   |
|   +-----------+-----------+     +-----------+------------+     +-------------+-------------+   |
|               |                             |                                |                 |
|               |                             v                                |                 |
|               |                 +-----------+------------+                   |                 |
|               +---------------->|     Detection Methods  |<------------------+                 |
|                                 | - RSS/Atom Monitor     |                                     |
|                                 | - XML Sitemap Monitor  |                                     |
|                                 | - Direct Page Monitor  |                                     |
|                                 +-----------+------------+                                     |
|                                             |                                                  |
|                                             v                                                  |
|                                 +-----------+------------+                                     |
|                                 |   Article Extractor    |                                     |
|                                 | (Trafilatura + JSON-LD)|                                     |
|                                 +-----------+------------+                                     |
|                                             |                                                  |
|                                             v                                                  |
|                                 +-----------+------------+                                     |
|                                 |  Delay Calc & Dedupe   |                                     |
|                                 +-----------+------------+                                     |
|                                             |                                                  |
+---------------------------------------------+--------------------------------------------------+
                                              |
                                              v
                                  +-----------+------------+
                                  |   SQLite / PostgreSQL  |
                                  | (Competitors, Articles,|
                                  |  Checks, Notifications)|
                                  +------------------------+
```

---

## Features

1. **Automatic Website Analyzer**:
   - Provide a competitor root URL (e.g. `https://stripe.com` or `http://127.0.0.1:8001`).
   - Automatically checks for RSS and Atom `<link>` tags and common feed endpoints (`/feed`, `/rss.xml`, `/atom.xml`).
   - Parses `robots.txt` and XML sitemaps (`/sitemap.xml`, sitemap indexes, and nested child sitemaps).
   - Scans navigation and homepage anchors to detect blog root pages (`/blog`, `/news`, `/articles`, `/insights`).
   - Inspects JSON-LD structured data (`Article`, `BlogPosting`), OpenGraph tags, canonical tags, and publication timestamps.
   - Automatically selects the optimal monitoring strategy (`RSS + Sitemap`, `RSS`, `Sitemap + Direct Page`, or `Direct Page`).

2. **Multi-Strategy Detection Engine**:
   - **RSS / Atom Monitor**: Parses entries with `feedparser`, extracts deep web article information, and tracks new posts.
   - **XML Sitemap Monitor**: Handles sitemap indexes and child sitemaps, extracting `<loc>` and `<lastmod>` timestamps.
   - **Direct Page Monitor**: Analyzes blog card links, semantic `<article>` containers, and URL paths without fragile CSS selectors.

3. **Article Extraction & Semantic Cleansing**:
   - Extracts title, author, publication date, featured image, categories, tags, and sanitized HTML content using `trafilatura` and `BeautifulSoup4`.
   - Never invents missing publication dates; stores missing dates as `null` with explicit `"Publication time unavailable"` indicators.

4. **Exact Detection Delay & 5-Minute Performance Target**:
   - Calculates exact delay down to the second: `delay = detected_at - published_at`.
   - Never rounds to generic approximations (e.g. outputs `"42 seconds"`, `"2 minutes 15 seconds"`).
   - Performance badges: **GREEN** (<= 5 minutes SLA) vs **YELLOW** (> 5 minutes).

5. **Duplicate Prevention**:
   - Enforces unique canonical URL indexing at the database level and normalizes URL query parameters (removes `utm_*`, `fbclid`, and tracking noise).
   - Prevents duplicate detection across repeated polling cycles and across multiple strategies.

6. **Continuous Background Scheduler & Concurrency Isolation**:
   - Driven by APScheduler `AsyncIOScheduler` with an `asyncio.Semaphore` worker pool.
   - Fault isolation: A slow, rate-limited, or failing website (DNS failure, HTTP 429, 504 timeout) is recorded as a `FAILED` check in the audit log and does not block other competitor checks.

7. **100-Website Concurrency Benchmark**:
   - Includes a dedicated Scale Test page demonstrating asynchronous worker pool handling of 100 competitor sites simultaneously with real-time throughput and latency metrics.

8. **Controlled Demo Target (`/demo-site`)**:
   - A standalone mock competitor site equipped with home, blog, JSON-LD posts, live RSS feed (`/rss.xml`), live XML sitemap (`/sitemap.xml`), and a 1-click **Publish New Test Article** control panel to demonstrate live discovery and instant delay calculation.

---

## Requirements

- **Python**: Version 3.10 or higher
- **Node.js**: Version 18.x or higher
- **npm**: Version 9.x or higher

---

## Installation & Setup

### 1. Clone or Navigate to the Project

```bash
cd competitor-blog-spy
```

### 2. Backend Installation

Navigate to the `backend/` directory and install the Python dependencies:

```bash
cd backend
python -m pip install -r requirements.txt
```

Create your local `.env` configuration file from the example:

```bash
# On Windows (PowerShell):
Copy-Item ..\.env.example .env

# On macOS/Linux:
cp ../.env.example .env
```

### 3. Frontend Installation

Navigate to the `frontend/` directory and install the Node packages:

```bash
cd ../frontend
npm install
```

---

## Running the Application

For a complete local testing setup, open three terminal tabs:

### Terminal 1: Launch Controlled Demo Website (Port 8001)

The controlled demo website represents an external competitor website you wish to spy on:

```bash
# From competitor-blog-spy root:
python -m uvicorn demo-site.server:app --port 8001
```

- Demo Website Home: `http://127.0.0.1:8001/`
- Demo Blog: `http://127.0.0.1:8001/blog`
- Demo RSS Feed: `http://127.0.0.1:8001/rss.xml`
- Demo Sitemap: `http://127.0.0.1:8001/sitemap.xml`
- Demo Control Panel: `http://127.0.0.1:8001/control`

### Terminal 2: Launch FastAPI Backend (Port 8000)

```bash
# From competitor-blog-spy root:
# Windows (PowerShell):
$env:PYTHONPATH="."
python -m uvicorn backend.main:app --port 8000 --reload

# macOS/Linux:
PYTHONPATH=. python -m uvicorn backend.main:app --port 8000 --reload
```

- REST API Documentation: `http://127.0.0.1:8000/docs`
- System Health Status: `http://127.0.0.1:8000/api/system/status`

### Terminal 3: Launch React Frontend (Port 5173)

```bash
# From competitor-blog-spy/frontend:
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

- Open the Dashboard: `http://127.0.0.1:5173/`

---

## How to Demonstrate Live Detection (Step-by-Step)

1. Open `http://127.0.0.1:5173/` in your browser.
2. In the top navigation bar, click **Quick Demo Competitor**.
   - The system automatically registers `http://127.0.0.1:8001` as a competitor.
   - The Website Analyzer scans the demo site, identifies the RSS feed (`/rss.xml`), sitemap (`/sitemap.xml`), and blog (`/blog`), and selects the strategy **RSS + Sitemap**.
3. In the sidebar, click **Demo Controller** (or navigate to `http://127.0.0.1:8001/control`).
4. Click **Publish Test Article Now**.
   - A new article with the current timestamp is published to the demo site.
5. In the BlogSpy dashboard, click **Run Checks Now** (or wait for the continuous background scheduler).
6. **Observe the Results**:
   - The new article is immediately detected!
   - The **Detection Delay Badge** displays the exact elapsed time (e.g. `2 seconds` or `14 seconds`) with an `EXCELLENT (<= 5 min)` green badge.
   - A **Notification** appears in the top-right notification center.
   - Clicking the article opens the **Article Reader Modal**, showing the extracted author, tags, canonical URL, and body content.
   - Clicking **Check Now** again verifies **Duplicate Prevention** (`0 new articles added`).

---

## 100-Website Concurrency Benchmark

To test how the system scales to 100 concurrent websites:

1. Click **Scale Test (100 Sites)** in the sidebar navigation.
2. Set the target count to `100` and workers to `15`.
3. Click **Launch 100-Site Test**.
4. Watch the real-time metrics update:
   - Queue size, active worker fibers, completed tasks, and isolated failures.
   - Latency distribution and throughput (exceeding 100 checks/sec).
   - Live streaming task logs showing isolated network latencies.

---

## Running Automated Tests

Run the complete test suite (13 unit and integration tests) using `pytest`:

```bash
# From competitor-blog-spy root:
# Windows (PowerShell):
$env:PYTHONPATH="."
pytest -v tests

# macOS/Linux:
PYTHONPATH=. pytest -v tests
```

### Running the Live Integration Verification Script

Run the automated live script that tests all 20 requirements against the running server:

```bash
python backend/verify_live_system.py
```

---

## REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/competitors` | GET | List all monitored competitors with article counts |
| `/api/competitors` | POST | Add competitor & trigger automatic website investigation |
| `/api/competitors/{id}` | GET | Get competitor details & discovered configuration |
| `/api/competitors/{id}` | PUT | Update competitor configuration or toggle monitoring |
| `/api/competitors/{id}` | DELETE | Delete competitor and associated data |
| `/api/competitors/{id}/analyze` | POST | Re-run automatic source discovery |
| `/api/competitors/{id}/check` | POST | Trigger immediate detection check |
| `/api/articles` | GET | List ingested articles (filterable by competitor, method, search) |
| `/api/articles/{id}` | GET | Get full extracted article content, images, and links |
| `/api/monitoring/history` | GET | List monitoring check execution logs and errors |
| `/api/dashboard/stats` | GET | Retrieve 7 dashboard summary metric cards |
| `/api/analytics` | GET | Performance charts (delays, method distribution, trends) |
| `/api/notifications` | GET | List detection alert notifications |
| `/api/scale-test/start` | POST | Launch 100-website concurrency simulation |
| `/api/scale-test/status` | GET | Stream live scale test benchmark metrics |
| `/api/demo/seed` | POST | 1-Click register controlled demo competitor |
| `/api/demo/publish-test-article` | POST | Publish new test article on demo competitor site |

---

## Troubleshooting

- **Port in use error**: If port 8000, 8001, or 5173 is already in use, terminate any old Python or Node processes (`Stop-Process -Name python, node -Force` on Windows or `killall python node` on Unix) or change the `--port` flag.
- **SQLite Database Locked**: SQLite with WAL mode handles concurrency cleanly. If you ever want to reset the database to a blank state, simply stop the backend, delete `blog_spy.db`, and restart the backend.
- **Live detection delay displays seconds**: That is by design! The platform calculates exact detection delay down to the second rather than rounding to generic approximations.
