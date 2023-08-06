#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys
import requests
import json

import gitlab

from DustCli.utils.git_token import get_token

class Api(object):

    def __init__(self, project_name):
        project_name = project_name.replace('/', '%2F')
        self.gl = gitlab.Gitlab('https://git.souche-inc.com', get_token(), api_version='4')
        self.project = self.gl.projects.get(project_name)

    # 提MR
    def create_mr(self, source_branch, target_branch, title):
        return self.project.mergerequests.create({'source_branch':source_branch,'target_branch':target_branch,'title':title})
        

if __name__ == "__main__":
    api = Api('1029')
    result = api.create_mr('test','devxx','Just Test')
    print(result)