# -*- coding: utf-8 -*-
"""Report AWS Lambdas running a deprecated engine."""

from logging import getLogger
import sys
from re import match
import click
from prettytable import PrettyTable

from classes.csv_file import CsvHandler
from classes.trusted_advisor import TrustedAdvisor
from classes.arn_handler import ArnHandler
from classes.python_sdk import AwsSession, AwsPythonSdk
from classes.python_arrays import GetItemFrom
from classes.looper import Looper

from helpers import config

LOGGER = getLogger(__name__)


def accounts_to_query(account_id: str) -> list:
    """Return a list with the AWS account/s where the query will run."""
    # List of active AWS accounts in the Org
    accounts = AwsPythonSdk(config.ROOT_ACCOUNT_ID, 'organizations').org_accounts()
    if account_id != '111111111111':
        # check if the selected account belongs to the Org
        accounts = [GetItemFrom(accounts).by_key_pair('AccountId', account_id)]
        if accounts == [None]:
            LOGGER.error("Account ID %s does not exist in the Organization.", account_id)
            sys.exit(-1)

    return accounts


def query(aws: dict) -> list:
    """List Trusted Advisor flagged resources per AWS account."""
    ta_check = TrustedAdvisor(
        AwsPythonSdk(aws['AccountId'], 'support', 'us-east-1').client(),
        'security',
        'AWS Lambda Functions Using Deprecated Runtimes'
        # 'cost_optimizing',
        # 'Underutilized Amazon EBS Volumes'
    )

    csv_rows = []
    for r in ta_check.resources():
        # pprint(r)
        #
        # resource example for AWS Lambda Functions Using Deprecated Runtimes:
        #
        # ['Red',
        #  'us-west-2',
        #  'arn:aws:lambda:us-west-1:11111111111111:function:lambda_function_name:1',
        #  'nodejs10.x',
        #  '-720',
        #  '07/30/2021',
        #  '3.0',
        #  '2023-07-20T08:00:00.000Z']
        #
        lambda_arn = ArnHandler(r[2])
        if lambda_arn.resource_version() == '$LATEST':
            csv_rows.append(
                [aws['AccountAlias'], r[1], r[0], lambda_arn.resource_id(), r[3], r[4]]
            )

    return csv_rows


def display_deprecated_lambdas(check_name: str, headers: list, findings: list) -> None:
    """Display Trusted Advisor findings - Deprecated lambdas."""
    pt = PrettyTable(headers)

    pt.align['AWS Account'] = 'l'
    pt.align['Region'] = 'l'
    pt.align['Lambda function'] = 'l'
    pt.align['Engine'] = 'l'
    pt.align['Expire_in'] = 'r'

    for finding in findings:
        pt.add_row(finding)

    pt.sortby = 'AWS Account'

    print(pt.get_string(title=check_name))


def aws_account_id_callback(ctx, param, value):  # pylint: disable=W0613
    """Validate AWS Account ID is valid."""
    if match(r'\d{12}', value) and len(value) == 12:
        return value

    raise click.BadParameter('AWS account ID must be 12 digits.')


@click.command()
@click.option(
    '-a',
    '--account',
    default='111111111111',
    show_default=False,
    nargs=1,
    type=str,
    callback=aws_account_id_callback,
    help='AWS Account ID to run the query on.'
)
def run_query(account: str) -> None:
    """Run an AWS Trusted Advisor query."""
    config.SESSION = AwsSession(config.CLI_PROFILE).cli()

    check_name = 'AWS Lambda Functions Using Deprecated Runtimes'
    headers = ['AWS Account', 'Region', 'Status', 'Lambda function', 'Engine', 'Expire_in']
    findings = Looper(accounts_to_query(account), query).parallel_return(summary=True)

    if click.confirm('Do you want to display the query on screen', default=True):
        display_deprecated_lambdas(check_name, headers, findings)
    else:
        file_name = config.CSV_PATH + 'deprecated_lambdas'
        print(f"\nSaving the report: {file_name}\n")
        csv_file = CsvHandler(file_name)
        csv_file.writer(findings, headers)


if __name__ == '__main__':
    run_query()  # pylint: disable=E1120
