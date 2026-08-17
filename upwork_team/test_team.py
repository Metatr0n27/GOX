import unittest
from team import Job, build_packet, rank_jobs


class TestUpworkRevenueTeam(unittest.TestCase):
    def test_youtube_job_scores_high(self):
        job = Job(
            title="Automated YouTube Video Creation Pipeline",
            description="Build an end-to-end workflow using n8n, Python and AI automation.",
            budget="$150 fixed",
        )
        packet = build_packet(job)
        self.assertGreaterEqual(packet.score, 70)
        self.assertIn("YouTube", packet.job_title)
        self.assertIn("approved_upwork_interface_required", packet.submission_status)

    def test_property_workflow_gets_specific_proposal(self):
        job = Job(
            title="AI Automation Engineer for Property Management Maintenance Workflow",
            description="Use n8n and OpenAI to classify tenant maintenance requests and route work orders.",
            budget="$75 - $100/hour",
        )
        packet = build_packet(job)
        self.assertIn("AppFolio/email requests", packet.proposal)
        self.assertIn("lower-middle", packet.bid_strategy)

    def test_ranking_prefers_stronger_fit(self):
        jobs = [
            Job("Generic senior architect", "10+ years enterprise architecture", "$100/hour"),
            Job("n8n Python automation", "n8n Python API workflow automation", "$50/hour"),
        ]
        ranked = rank_jobs(jobs)
        self.assertEqual(ranked[0]["job_title"], "n8n Python automation")


if __name__ == "__main__":
    unittest.main()
