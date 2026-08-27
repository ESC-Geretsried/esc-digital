import importlib.util
from pathlib import Path
import unittest

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

    def test_generated_artifacts_match(self):
        OWML.generate(check=True)


if __name__ == "__main__":
    unittest.main()
