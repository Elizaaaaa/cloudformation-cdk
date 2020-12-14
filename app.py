#!/usr/bin/env python3

from aws_cdk import core

from update_matrics.update_matrics_stack import UpdateMatricsStack

from parse_config_file import get_alarms

names, dimensions = get_alarms()
props = {}

app = core.App()
UpdateMatricsStack(app, "update-matrics")

app.synth()
