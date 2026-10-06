import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Set, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.competitor import Competitor
from backend.models.article import Article
from backend.models.monitoring_check import MonitoringCheck
from backend.models.notification import Notification
from backend.services.rss_monitor import RSSMonitor
from backend.services.sitemap_monitor import SitemapMonitor
from backend.services.page_monitor import PageMonitor
from backend.utils.date_helpers import format_detection_delay

logger = logging.getLogger(__name__)

class DetectionEngine:
    """
    Central Detection Engine.
    Executes checks per competitor, handles multi-strategy execution,
    guarantees strict duplicate prevention, persists articles, records checks,
    and creates dashboard notifications.
    """

    def __init__(self, db: Session):
        self.db = db
        self.rss_monitor = RSSMonitor()
        self.sitemap_monitor = SitemapMonitor()
        self.page_monitor = PageMonitor()

    async def run_check_for_competitor(self, competitor_id: int) -> MonitoringCheck:
        competitor = self.db.query(Competitor).filter(Competitor.id == competitor_id).first()
        if not competitor:
            raise ValueError(f"Competitor ID {competitor_id} not found.")

        started_at = datetime.now(timezone.utc)
        start_time_perf = time.perf_counter()
        
        # Load all existing URLs across database to prevent cross-source duplicates
        existing_canonical_records = self.db.query(Article.canonical_url).all()
        existing_source_records = self.db.query(Article.source_url).all()
        existing_urls: Set[str] = {r[0] for r in existing_canonical_records if r[0]} | {r[0] for r in existing_source_records if r[0]}

        strategy = competitor.selected_strategy or "Automatic"
        status = "SUCCESS"
        error_message = None
        articles_found = 0
        new_articles_list: List[Dict[str, Any]] = []
        methods_used = []

        try:
            # RSS Strategy execution
            if ("RSS" in strategy or strategy == "Automatic") and (competitor.rss_url or (competitor.configuration and competitor.configuration.rss_url)):
                feed_url = competitor.rss_url or competitor.configuration.rss_url
                methods_used.append("RSS")
                try:
                    res = await self.rss_monitor.check_feed(feed_url, existing_urls)
                    articles_found += res["articles_found"]
                    new_articles_list.extend(res["new_articles"])
                except Exception as rss_err:
                    logger.warning(f"RSS check failed for {competitor.name}: {rss_err}")
                    if "Sitemap" not in strategy and "Page" not in strategy:
                        raise rss_err

            # Sitemap Strategy execution
            if ("Sitemap" in strategy or (strategy == "Automatic" and not new_articles_list)) and (competitor.sitemap_url or (competitor.configuration and competitor.configuration.sitemap_url)):
                sitemap_url = competitor.sitemap_url or competitor.configuration.sitemap_url
                methods_used.append("Sitemap")
                try:
                    res = await self.sitemap_monitor.check_sitemap(sitemap_url, existing_urls)
                    articles_found += res["articles_found"]
                    new_articles_list.extend(res["new_articles"])
                except Exception as sitemap_err:
                    logger.warning(f"Sitemap check failed for {competitor.name}: {sitemap_err}")
                    if not methods_used or len(methods_used) == 1:
                        if "Direct Page" not in strategy:
                            raise sitemap_err

            # Direct Page Strategy execution
            if ("Direct Page" in strategy or (strategy == "Automatic" and not new_articles_list)) and (competitor.blog_url or (competitor.configuration and competitor.configuration.blog_url)):
                blog_url = competitor.blog_url or competitor.configuration.blog_url
                methods_used.append("Direct Page")
                try:
                    res = await self.page_monitor.check_page(blog_url, existing_urls)
                    articles_found += res["articles_found"]
                    new_articles_list.extend(res["new_articles"])
                except Exception as page_err:
                    logger.warning(f"Direct Page check failed for {competitor.name}: {page_err}")
                    if not new_articles_list and not articles_found:
                        raise page_err

        except Exception as exc:
            status = "FAILED"
            error_message = str(exc)
            logger.error(f"Detection failed for competitor {competitor.name}: {exc}")

        completed_at = datetime.now(timezone.utc)
        response_time_ms = round((time.perf_counter() - start_time_perf) * 1000, 2)

        # Persist newly discovered articles with duplicate protection
        new_saved_count = 0
        method_str = " + ".join(dict.fromkeys(methods_used)) if methods_used else strategy

        if status != "FAILED":
            for art in new_articles_list:
                # Double-check database existence
                canonical = art["canonical_url"]
                existing_art = self.db.query(Article).filter(
                    (Article.canonical_url == canonical) | (Article.source_url == art["source_url"])
                ).first()
                if existing_art:
                    continue

                article_obj = Article(
                    competitor_id=competitor.id,
                    title=art["title"],
                    content=art.get("content"),
                    author=art.get("author"),
                    published_at=art.get("published_at"),
                    detected_at=art.get("detected_at", completed_at),
                    detection_delay_seconds=art.get("detection_delay_seconds"),
                    detection_method=art.get("detection_method", "Unknown"),
                    canonical_url=canonical,
                    source_url=art["source_url"],
                    meta_description=art.get("meta_description"),
                    featured_image=art.get("featured_image"),
                    categories=art.get("categories"),
                    tags=art.get("tags"),
                    relevant_links=art.get("relevant_links"),
                )

                try:
                    self.db.add(article_obj)
                    self.db.flush()
                    new_saved_count += 1

                    # Create Notification
                    delay_fmt = format_detection_delay(art.get("detection_delay_seconds"))
                    notif = Notification(
                        competitor_id=competitor.id,
                        article_id=article_obj.id,
                        title=f"New article detected from {competitor.name}",
                        message=f"'{article_obj.title}' was detected via {article_obj.detection_method} (Delay: {delay_fmt}).",
                        detection_method=article_obj.detection_method,
                        detection_delay_seconds=article_obj.detection_delay_seconds,
                    )
                    self.db.add(notif)
                except IntegrityError:
                    self.db.rollback()
                    logger.info(f"Duplicate prevented by DB unique constraint for {canonical}")
                    continue

        # Record MonitoringCheck
        check = MonitoringCheck(
            competitor_id=competitor.id,
            started_at=started_at,
            completed_at=completed_at,
            status=status,
            detection_method=method_str,
            articles_found=articles_found,
            new_articles_found=new_saved_count,
            response_time_ms=response_time_ms,
            error_message=error_message,
        )
        self.db.add(check)

        # Update Competitor tracking status
        competitor.last_checked_at = completed_at
        if status == "SUCCESS":
            competitor.monitoring_status = "ONLINE"
            if new_saved_count > 0:
                competitor.last_successful_detection_at = completed_at
        else:
            competitor.monitoring_status = "ERROR"

        try:
            self.db.commit()
            self.db.refresh(check)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error committing monitoring check: {e}")

        return check
