# Query AWS Lambdas running on a deprecated software version

Use Python boto3 module, AWS SDK for Python, to run a CLI query to identify Deprecated Lambdas within
an AWS Organization.

## Required Python modules

* boto3
* botocore
* click
* prettytable

**Note:** Check the `requirements.txt` file in case you have some package version issue.

## Pre-requisite

* A valid AWS cli profile (either SSO or IAM user)

## Consider to install pre-commit

If you are planning to enhance this code it is highly recommended to install [pre-commit](https://pre-commit.com/index.html)
 to speed up development and keep some standard coding style.

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## Query AWS Resources

This python script will run the query across all enabled regions in an Organization using parallel
processing code, it certainly runs fast though.

Please update your specific AWS Organization settings in the `helpers/config.py` file before run it:

```bash
python deprecated_lambdas_query.py --help

Usage: deprecated_lambdas_query.py [OPTIONS]

  Run an AWS Trusted Advisor query.

Options:
  -a, --account TEXT  AWS Account ID to run the query on.
  --help              Show this message and exit.

```

## Author and Lincense

This script has been written by [Ariel Jall](https://github.com/ArielJalil) and it is released under
 [GNU 3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).
