from aws_cdk import core, aws_cloudwatch

metric_names = {
    "tensorflow2.3":{
        "bert":{
            "Loss": "Bert Loss",
            "Throughput": "Bert Tokens/second",
            "Duration": "Bert Time_to_train"
        },
        "gpt2":{
            "Loss": "GPT2 Train_loss",
            "Duration": "GPT2 Time_to_train"
        }
    },
    "pytorch":{
        "bert":{
            "Loss": "Bert Loss",
            "Throughput": "Bert Sequences/second",
            "Duration": "Bert Time_to_train"
        },
        "t5":{
            "Loss": "T5 Loss",
            "Duration": "T5 Time_to_train"
        }
    }
}
namespace = "ModelParallelism"
period = core.Duration.days(1)

class UpdateMatricsStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        for frame_model in props:
            framework, model = frame_model.split("_")
            names = props[frame_model]["Names"]
            dimensions = props[frame_model]["Dimensions"]
            
            for i, alarm_name_group in enumerate(names):
                for j, name in enumerate(alarm_name_group):
                    dimension = dimensions[i][j]

                    metric_name = metric_names[framework][model.lower()][name.split('-')[-1]]
                    print(metric_name)
                    metric = aws_cloudwatch.Metric(metric_name=metric_name,
                                                    namespace=namespace,
                                                    dimensions=dimension,
                                                    period=period,
                                                    statistic="avg")

                    print(f"{metric}\n")

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