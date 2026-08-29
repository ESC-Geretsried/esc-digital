import importlib.util
from datetime import datetime
import os
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "owml.py"
SPEC = importlib.util.spec_from_file_location("esc_owml", SCRIPT)
OWML = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(OWML)


class OWMLTests(unittest.TestCase):
    def test_every_current_route_has_exactly_one_instance(self):
        _, _, pages, _ = OWML.validate()
        self.assertEqual(set(pages), OWML.content_routes())

    def test_all_used_nodes_have_renderer_coverage(self):
        catalog, patterns, pages, _ = OWML.validate()
        covered = {node["type"] for node in catalog["nodes"]}
        used = {node["type"] for page in pages.values() for node in OWML.expanded_nodes(patterns, page)}
        self.assertTrue(used <= covered)

    def test_team_sports_variants_are_fail_closed(self):
        _, patterns, pages, _ = OWML.validate()
        for route in OWML.NO_STANDINGS:
            self.assertNotIn("standings", [node["id"] for node in OWML.expanded_nodes(patterns, pages[route])])
        u15_nodes = [node["id"] for node in OWML.expanded_nodes(patterns, pages["/u15/"])]
        self.assertEqual(
            u15_nodes,
            ["header", "hero", "team-navigation", "sponsor-ticker", "overview", "roster",
             "team-staff", "news", "competition-link", "contacts", "footer"],
        )
        self.assertIn("competition-link", u15_nodes)
        self.assertTrue({"schedule", "standings", "results"}.isdisjoint(u15_nodes))
        river_rats_nodes = [node["id"] for node in OWML.expanded_nodes(patterns, pages["/river-rats/"])]
        self.assertTrue({"next-home-game", "schedule", "standings", "results"} <= set(river_rats_nodes))

    def test_founder_homepage_order_is_exact(self):
        _, patterns, pages, _ = OWML.validate()
        self.assertEqual(
            [node["id"] for node in OWML.expanded_nodes(patterns, pages["/"])],
            ["announcements", "header", "hero-rotation", "primary-entrances", "news",
             "sport-areas", "club-areas", "sponsor-ticker", "footer"],
        )

    def test_founder_homepage_behavior_invariants_are_canonical(self):
        _, patterns, _, _ = OWML.validate()
        invariants = set(patterns["homepage"]["invariants"])
        self.assertIn("youth-hero-daily-image-static-nachwuchs-link", invariants)
        self.assertIn("announcement-sequential-slow", invariants)
        self.assertIn("reduced-motion-static-announcement", invariants)

    def test_generated_artifacts_match(self):
        OWML.generate(check=True)

    def test_canonical_player_placeholder_is_available(self):
        placeholder = ROOT / "site/src/static/images/placeholders/player.png"
        resolver = (ROOT / "site/src/layouts/partials/player-image.html").read_text(encoding="utf-8")
        self.assertTrue(placeholder.is_file())
        self.assertIn("images/placeholders/player.png", resolver)

    def test_news_retention_uses_binding_policy_timezone(self):
        class FrozenDateTime:
            @classmethod
            def now(cls, timezone):
                self.assertEqual(timezone.key, "Europe/Berlin")
                return datetime(2026, 8, 29, 1, 30, tzinfo=timezone)

        with patch.object(OWML, "datetime", FrozenDateTime), patch.dict(
            os.environ, {"OWML_AS_OF_DATE": "", "NEWS_RETENTION_AS_OF": ""}
        ):
            self.assertFalse(OWML.article_retained("/aktuelles/2025-08-29-test/"))


if __name__ == "__main__":
    unittest.main()
