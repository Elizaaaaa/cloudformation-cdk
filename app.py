#!/usr/bin/env python3
import glob, os

from aws_cdk import core

from update_matrics.update_matrics_stack import UpdateMatricsStack
from update_matrics.parse_config_file import get_alarms


config_path = "./configs"

props = {}
for name in os.listdir(config_path):
    framework, model = name.split("_")
    print(f"Reading the config of {model} {framework}")
    path = os.path.join(config_path, name)
    alarm_names = []
    alarm_dimensions = []
    for config_file in os.listdir(path):
        names, dimensions = get_alarms(model, framework, path, config_file)
        alarm_names.append(names)
        alarm_dimensions.append(dimensions)
    
    props[name] = {"Names": alarm_names, "Dimensions": alarm_dimensions}

app = core.App()
UpdateMatricsStack(app, "update-matrics", props)

app.synth()
