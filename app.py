#!/usr/bin/env python3
import glob, os

from aws_cdk import core, aws_cloudwatch, aws_sns
import aws_cdk.aws_cloudwatch_actions as cw_actions

from update_matrics.cut_ticket import TicketAction

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
    alarm_thresholds = []
    for config_file in os.listdir(path):
        names, dimensions, thresholds = get_alarms(model, framework, path, config_file)
        alarm_names.append(names)
        alarm_dimensions.append(dimensions)
        alarm_thresholds.append(thresholds)
        break

    props[name] = {"Names": alarm_names, "Dimensions": alarm_dimensions, "Thresholds": alarm_thresholds}

app = core.App()

stack = UpdateMatricsStack(app, "update-matrics", props)
topic = aws_sns.Topic(stack, "Topic")
action = cw_actions.SnsAction(topic)
action = TicketAction(stack, "ticket-action")
print(action.to_string())
for alarm in stack.outputs:
    alarm.add_alarm_action(action)

# for alarm in stack.outputs:
#     alarm.add_alarm_action(action)

app.synth()
