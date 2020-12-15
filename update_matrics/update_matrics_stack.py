from aws_cdk import core, aws_cloudwatch
from parse_config_file import get_metric_name


namespace = "ModelParallelism"
period = core.Duration.days(1)

class UpdateMatricsStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        for frame_model in props:
            names = props[frame_model]["Names"]
            dimensions = props[frame_model]["Dimensions"]
            
            for i, alarm_name_group in enumerate(names):
                for j, name in enumerate(alarm_name_group):
                    dimension = dimensions[i][j]

                    print(name)
                    metric_name = get_metric_name(name)
                    metric = aws_cloudwatch.Metric(metric_name=metric_name,
                                                    namespace=namespace,
                                                    dimensions=dimension,
                                                    period=period,
                                                    statistic="avg")

                    print(f"{metric.to_string()}\n")

        # operator = aws_cloudwatch.ComparisonOperator.LessThanThreshold if "Throughput" in name \
        #         else aws_cloudwatch.ComparisonOperator.GreaterThanThreshold

        # alarm = aws_cloudwatch.Alarm(scope=self,
        #                             id=name,
        #                             alarm_description=f"The Model Parallelism alarm {name}.",
        #                             alarm_name=name,
        #                             comparison_operator=operator,
        #                             evaluation_periods=1,
        #                             metric=athena_workgroup_processed_bytes,
        #                             period=core.Duration.days(1),
        #                             statistic="sum",
        #                             threshold=ONE_TERABYTE_IN_BYTES,
        #                             treat_missing_data=aws_cloudwatch.TreatMissingData.NOT_BREACHING)