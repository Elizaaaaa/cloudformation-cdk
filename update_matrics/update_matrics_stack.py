from aws_cdk import core, aws_cloudwatch, aws_sns
import aws_cdk.aws_cloudwatch_actions as cw_actions
from parse_config_file import get_metric_name

from cut_ticket import TicketAction

namespace = "ModelParallelism"
period = core.Duration.days(1)

ticket_arn = "arn:aws:cloudwatch::cwa-internal:ticket:5:AWS:DeepEngine:Model+Parallelism:AWS+Model+Parallelism:"


class UpdateMatricsStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.alarms = []

        for frame_model in props:
            names = props[frame_model]["Names"]
            dimensions = props[frame_model]["Dimensions"]
            thresholds = props[frame_model]["Thresholds"]
            
            for i, alarm_name_group in enumerate(names):
                for j, name in enumerate(alarm_name_group):
                    if len(name)==0:
                        # Empty list due to missing metric
                        continue

                    dimension = dimensions[i][j][0]
                    threshold = thresholds[i][name.split("-")[-1]]

                    metric_name = get_metric_name(name)
                    metric = aws_cloudwatch.Metric(metric_name=metric_name,
                                                    namespace=namespace,
                                                    dimensions=dimension,
                                                    period=period,
                                                    statistic="avg")

                    operator = aws_cloudwatch.ComparisonOperator.LESS_THAN_LOWER_THRESHOLD if "Throughput" in name \
                            else aws_cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
                    
                    print(f"Currently working on {name}")
                    alarm = aws_cloudwatch.Alarm(scope=self,
                                                id=name,
                                                alarm_description=f"The Model Parallelism alarm {name}.",
                                                alarm_name=name,
                                                comparison_operator=operator,
                                                evaluation_periods=1,
                                                metric=metric,
                                                period=period,
                                                statistic="avg",
                                                threshold=threshold,
                                                treat_missing_data=aws_cloudwatch.TreatMissingData.NOT_BREACHING)
                    self.alarms.append(alarm)
                break
            break
    
    @property
    def outputs(self):
        return self.alarms
