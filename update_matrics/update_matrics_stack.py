from aws_cdk import core, aws_cloudwatch, aws_sns
from aws_cdk.aws_cloudwatch import TextWidget, GraphWidget
import aws_cdk.aws_cloudwatch_actions as cw_actions
from parse_config_file import get_metric_name

from cut_ticket import TicketAction

namespace = "ModelParallelism"
period = core.Duration.days(1)

# Widget Definitions
width = 100
height = 100
pos = [0, 0]

class UpdateMatricsStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.alarms = []

        for frame_model in props:
            names = props[frame_model]["Names"]
            dimensions = props[frame_model]["Dimensions"]
            thresholds = props[frame_model]["Thresholds"]
            
            # Get Dashboard
            dashboard_name = f"ModelParallelism-{frame_model.split('_')[1]}-Test"
            dashboard = aws_cloudwatch.Dashboard(scope=self,
                                                 id=dashboard_name,
                                                 dashboard_name=dashboard_name)
            
            for i, alarm_name_group in enumerate(names):
                if len(alarm_name_group)==0:
                    # Empty list due to missing metric
                    continue

                # Add Dashboard Text Widget
                name = alarm_name_group[0]
                platform = "EC2" if "EC2" in name else "SageMaker"
                dashboard.add_widgets(TextWidget(
                                    markdown=f"# Platform: {platform}\n## Trigger Period: {name.split('-')[1]}",
                                        ))

                for j, name in enumerate(alarm_name_group):
                    dimension = dimensions[i][j][0]
                    threshold = thresholds[i][name.split("-")[-1]]

                    metric_name = get_metric_name(name)
                    metric = aws_cloudwatch.Metric(metric_name=metric_name,
                                                    namespace=namespace,
                                                    dimensions=dimension,
                                                    period=period,
                                                    statistic="avg")

                    # Update Dashboard Graph Widget
                    dashboard.add_widgets(GraphWidget(
                                            title=name.split("-")[-1],
                                            left=[metric]
                                        ))

                    # Update Alarm∂
                    operator = aws_cloudwatch.ComparisonOperator.LESS_THAN_LOWER_THRESHOLD if "Throughput" in name \
                            else aws_cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
                    
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
