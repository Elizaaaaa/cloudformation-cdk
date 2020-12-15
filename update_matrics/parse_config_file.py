import boto3
import os
import argparse
from datetime import datetime, timedelta

metrics = {"throughput":"Throughput", "loss":"Loss", "time_to_train":"Duration", "train_loss":"Loss"}
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
        "bertnonsequential": {
            "Loss": "BertNonSequential Loss",
            "Throughput": "BertNonSequential Sequences/second",
            "Duration": "BertNonSequential Time_to_train"
        },
        "t5":{
            "Loss": "T5 Loss",
            "Duration": "T5 Time_to_train"
        }
    }
}
instances = ["p3dn", "p4d"]

cloudwatch = boto3.client('cloudwatch', region_name="us-west-2")
sns_topic_group = "arn:aws:sns:us-west-2:578276202366:rubik-sns-topic"
namespace = "ModelParallelism"
period = 60 * 60 * 24
retry_fetch_days = 10

def get_metric_name(name):
    f = "tensorflow2.3" if "TF" in name else "pytorch"
    model = name.split("-")[2].lower()
    metric = name.split('-')[-1]

    if "NonSquential" in name:
        model += "nonsequential"

    metric_name = metric_names[f][model][metric]
    return metric_name


def get_alarm_name(model_name, framework_name, instance, config_file, metric_name):
    dimensions = []
    # pipeline: Commit, Nightly, Canary
    pipeline = ""
    if "canary" in config_file:
        pipeline = "-Canary"
        dimensions.append({'Name': 'Pipeline Type', 'Value': 'canary'})
    elif "nightly" in config_file:
        pipeline = "-Nightly"
        dimensions.append({'Name': 'Pipeline Type', 'Value': 'nightly'})
    elif "convergence" in config_file:
        pipeline = "-Weekly"
        dimensions.append({'Name': 'Pipeline Type', 'Value': 'weekly'})
    else:
        pipeline = "-Commit"
        dimensions.append({'Name': 'Pipeline Type', 'Value': 'commit'})
    # model: BERT, GPT2, T5
    model = ""
    if "bert" in model_name.lower():
        model = "-BERT"
    elif "gpt2" in model_name.lower():
        model = "-GPT2"
    elif "t5" in model_name.lower():
        model = "-T5"
    else:
        raise ValueError("Please provide a valid model name!")
    # framework: TF23, PyTorch
    framework = ""
    if "tensorflow" in framework_name:
        framework = "-TF23"
        dimensions.append({'Name': 'Docker Tag Name', 'Value': 'tensorflow2.3_test'})
    elif "pytorch" in framework_name:
        framework = "-PyTorch"
        dimensions.append({'Name': 'Docker Tag Name', 'Value': 'pytorch_test'})
    else:
        raise ValueError("Please provide a tag name contains tensorflow or pytorch!")
    # hvd
    hvd = ""
    # nodes:
    nodes = ""
    # bert sequential
    seq = ""
    if "horovod" in config_file:
        hvd = "-HVD"
        dimensions.append({'Name': 'Horovod', 'Value': 'True'})
        dimensions.append({'Name': 'Instance count', 'Value': '1'})
    elif "multi_node" in config_file:
        hvd = "-HVD"
        nodes = "-2Nodes"
        dimensions.append({'Name': 'Horovod', 'Value': 'True'})
        dimensions.append({'Name': 'Instance count', 'Value': '2'})
    elif "sequential" in config_file:
        seq = "-NonSequential"
        dimensions.append({'Name': 'Horovod', 'Value': 'False'})
        dimensions.append({'Name': 'Instance count', 'Value': '1'})
    else:
        dimensions.append({'Name': 'Horovod', 'Value': 'False'})
        dimensions.append({'Name': 'Instance count', 'Value': '1'})

    if "p4d" in instance:
        dimensions.append({'Name': 'Instance Type', 'Value': 'p4d.24xlarge'})
    elif "p3dn" in instance:
        dimensions.append({'Name': 'Instance Type', 'Value': 'p3dn.24xlarge'})
    else:
        dimensions.append({'Name': 'Instance Type', 'Value': 'p3.16xlarge'})

    name = f"Rubik{pipeline}{model}{framework}{hvd}{seq}{instance}{nodes}-{metric_name}"

    metric_name = get_metric_name(name)
    if not is_matric_exist(name, metric_name, dimensions):
        print(f"The alarm {name} does not have necessary cloudwatch value!")
        return [], []
    
    return name, dimensions


def is_matric_exist(alarm, metric_name, dimensions):
    has_data = False
    for i in range(1, retry_fetch_days):
        metric_data = cloudwatch.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': alarm.replace("-", "").lower(),
                        'MetricStat': {
                            'Metric': {
                                'Namespace': namespace,
                                'MetricName': metric_name,
                                'Dimensions': dimensions
                            },
                            'Period': period*i,
                            'Stat': 'Average',
                        },
                    }
                ],
                StartTime=datetime.now() - timedelta(seconds=period*i),
                EndTime=datetime.now(),
            )
        if (len(metric_data["MetricDataResults"][0]["Values"]) > 0):
            has_data = True
            break
    return has_data


def get_alarms(model, framework, path, config_file):
    fname = os.path.join(path, config_file)
    with open(fname, "r") as f:
        config = f.read()

    alarm_names = []
    metric_dimensions = []
    thresholds = {}
    
    for line in config.splitlines():
        metric_name = line.split(" = ")[0]
        if metric_name in metrics:
            metric_value = float(line.split(" = ")[1])
            thresholds[metrics[metric_name]] = metric_value

            if config_file == "single_node_nightly.ini":
                # only this config runs on different instance types
                for i in instances:
                    name, dimensions = get_alarm_name(model, framework, f"-{i}", config_file, metrics[metric_name])
                    alarm_names.append(name)
                    metric_dimensions.append(dimensions)
            elif config_file == "single_node_commit.ini":
                # create the EC2 alarms based on the single_node_commit,ini
                # ec2 tests only runs on nightly pipeline
                ec2_config = config_file.replace("commit", "nightly")
                # the dimension of EC2 test is different
                name, dimensions = get_alarm_name(model, framework, f"-EC2", ec2_config, metrics[metric_name])
                alarm_names.append(name)
                ec2_dimensions = []
                for d in dimensions:
                    if d["Name"] == "Docker Tag Name" or d["Name"] == "Instance Type":
                        ec2_dimensions.append(d)

                metric_dimensions.append(ec2_dimensions)
            
            name, dimensions = get_alarm_name(model, framework, "", config_file, metrics[metric_name])
            alarm_names.append(name)
            metric_dimensions.append(dimensions)
    
    return alarm_names, metric_dimensions, thresholds


