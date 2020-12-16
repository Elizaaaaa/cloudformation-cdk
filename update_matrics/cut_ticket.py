from aws_cdk import core, aws_cloudwatch


class TicketAction(aws_cloudwatch.IAlarmAction):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.alarmActionArn = "arn:aws:cloudwatch::cwa-internal:ticket:5:AWS:DeepEngine:Model+Parallelism:AWS+Model+Parallelism:"
