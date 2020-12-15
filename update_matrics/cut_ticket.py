from aws_cdk import core, aws_cloudwatch


class TicketAction(aws_cloudwatch.IAlarmAction):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.alarmActionArn = "arn:aws:cloudwatch::cwa-internal:ticket:5:AWS:DeepEngine:Model+Parallelism:AWS+Model+Parallelism:"
