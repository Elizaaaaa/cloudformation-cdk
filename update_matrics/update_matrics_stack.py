from aws_cdk import core, aws_cloudwatch, aws_sns
from aws_cdk.aws_cloudwatch import TextWidget, GraphWidget, Color
import aws_cdk.aws_cloudwatch_actions as cw_actions
from parse_config_file import get_metric_name, is_matric_exist

from cut_ticket import TicketAction

namespace = "ModelParallelism"
period = core.Duration.days(1)

class UpdateMatricsStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.alarms = []
        # Widget Definitions
        self.widget_x = 0
        self.widget_y = 0
        self.graph_height = 0

        frame_model = "tensorflow2.3_GPT2"

        if frame_model == "tensorflow2.3_GPT2":
            names = props[frame_model]["Names"]
            dimensions = props[frame_model]["Dimensions"]
            thresholds = props[frame_model]["Thresholds"]
            
            # Get Dashboard
            dashboard_name = f"ModelParallelism-{frame_model.split('_')[1]}-Test"
            print(f"Creating dashboard {dashboard_name}")
            dashboard = aws_cloudwatch.Dashboard(scope=self,
                                                 id=dashboard_name,
                                                 dashboard_name=dashboard_name)
            
            for i, alarm_name_group in enumerate(names):
                print(f"Start on {alarm_name_group}")
                # Add Dashboard Text Widget
                name = alarm_name_group[0]
                platform = "EC2" if "EC2" in name else "SageMaker"
                text = TextWidget(
                                markdown=f"# Platform: {platform}\n## Trigger Period: {name.split('-')[1]}"
                                )
                dashboard.add_widgets(text)
                self.widget_y += text.height

                for j, name in enumerate(alarm_name_group):
                    dimension = dimensions[i][j]
                    print(f"check the {dimension}")
                    threshold = thresholds[i][name.split("-")[-1]]

                    metric_name = get_metric_name(name)
                    if not is_matric_exist(name, metric_name, dimension):
                        print(f"The alarm {name} does not have necessary cloudwatch value!")
                        continue

                    metric = aws_cloudwatch.Metric(metric_name=metric_name,
                                                    namespace=namespace,
                                                    dimensions=dimension,
                                                    period=period,
                                                    statistic="avg")

                    # Update Dashboard Graph Widget
                    graph = GraphWidget(
                                    title=name.split("-")[-1],
                                    left=[metric],
                                    left_annotations=[{"value": threshold, "label": "Threshold", "color": Color.RED}]
                                )
                    graph.position(self.widget_x, self.widget_y)
                    graph_height = graph.height
                    self.widget_x += graph.width
                    
                    graph.add_left_metric(metric)
                    dashboard.add_widgets(graph)

                    # Update Alarm
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
                self.widget_y += graph_height
                self.widget_x = 0
                
                break
            
    
    @property
    def outputs(self):
        return self.alarms
