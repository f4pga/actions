#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier:	ISC

"""Module creating a Pull Request on GitHub."""

from datetime import datetime
import json
from os import environ
import sys

import requests


def create_pull_request(gh_repo: str, gh_token: str, pr_base: str,
                        pr_head: str, pr_title: str, pr_body: str = ''):
    """Creates a Pull Request on GitHub."""

    response = requests.post(
            'https://api.github.com/repos/' + gh_repo + '/pulls',
            headers={
                'Authorization': 'token ' + gh_token,
                'Accept': 'application/vnd.github.v3+json',
                },
            json={
                'base':  pr_base,
                'body':  pr_body,
                'head':  pr_head,
                'title': pr_title,
                },
            )
    if response.status_code != 201:
        print('ERROR: Pull Request creation failed with status: '
              + str(response.status_code) + ' ' + response.reason)
        print()
        print('GitHub API response data was:')
        json.dump(response.json(), sys.stdout, indent=2)
        print()
        sys.exit(1)
    else:
        print('Pull Request created successfully!')
        print("It's available at: " + response.json()['html_url'])


if __name__ == '__main__':
    pr_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    body = f"""
Pull Request created by the `{environ['GITHUB_WORKFLOW']}` workflow.

If this Pull Request should have triggered CI workflows but it hasn't, make sure that the token passed with `gh_access_token` input to the `update_conda_lock` action is a [Personal Access Token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token). PR Checks cannot be triggered using a common `secrets.GITHUB_TOKEN`. Still, do pass *PAT* as an [encrypted secret](https://docs.github.com/en/actions/reference/encrypted-secrets) for security reasons.
    """.strip()

    create_pull_request(
        environ['GITHUB_REPOSITORY'],
        environ['GH_ACCESS_TOKEN'],
        environ['PR_BASE'],
        environ['PR_HEAD'],
        environ['PR_TITLE_CORE'] + ' ' + pr_time,
        pr_body=body,
    )
