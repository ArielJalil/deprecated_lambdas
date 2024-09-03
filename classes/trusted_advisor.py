# -*- coding: utf-8 -*-
"""Class to handle Trusted Advisor findings."""

from logging import getLogger
LOGGER = getLogger(__name__)


class TrustedAdvisor:
    """Manage CloudWatch Metric."""

    def __init__(self, client: object, category: str, check: str) -> None:
        """Set class variables.

        Boto3 client needs to be 'support' within 'us-east-1' region
        Categories: [ cost_optimizing | security | fault_tolerance | performance | service_limits ]
        Check is the title you see in Trusted advisor console i.e. Underutilized Amazon EBS Volumes
        """
        self.client = client
        self.category = category
        self.check = check

    def checks(self) -> list:
        """Fetch Trusted Advisor checks by category."""
        try:
            checks = self.client.describe_trusted_advisor_checks(language='en')
        except:  # pylint: disable=W0702
            return []

        checks_by_category = [x for x in checks['checks'] if x['category'] == self.category]

        return checks_by_category

    def check_ids(self) -> list:
        """Get a list of check IDs per check title."""
        return [x['id'] for x in self.checks() if x['name'] == self.check]

    def resources(self) -> any:
        """Get flagged resources per check_title."""
        for check_id in self.check_ids():
            check = self.client.describe_trusted_advisor_check_result(
                checkId=check_id,
                language='en'
            )
            for resource in check['result']['flaggedResources']:
                yield resource['metadata']
