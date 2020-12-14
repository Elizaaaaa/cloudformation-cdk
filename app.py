#!/usr/bin/env python3

from aws_cdk import core

from update_matrics.update_matrics_stack import UpdateMatricsStack


app = core.App()
UpdateMatricsStack(app, "update-matrics")

app.synth()
