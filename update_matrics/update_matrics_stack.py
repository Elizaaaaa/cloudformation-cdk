from aws_cdk import core, aws_cloudwatch


class UpdateMatricsStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        metrics = aws_cloudwatch.Metric(metric_name=name,
                                        namespace=namespace,
                                        dimensions=dimensions,
                                        statistic="avg")

        operator = aws_cloudwatch.ComparisonOperator.LessThanThreshold if "Throughput" in name 
                else aws_cloudwatch.ComparisonOperator.GreaterThanThreshold

        alarm = aws_cloudwatch.Alarm(scope=self,
                                    id=name,
                                    alarm_description=f"The Model Parallelism alarm {name}.",
                                    alarm_name=name,
                                    comparison_operator=operator,
                                    evaluation_periods=1,
                                    metric=athena_workgroup_processed_bytes,
                                    period=core.Duration.days(1),
                                    statistic="sum",
                                    threshold=ONE_TERABYTE_IN_BYTES,
                                    treat_missing_data=aws_cloudwatch.TreatMissingData.NOT_BREACHING)