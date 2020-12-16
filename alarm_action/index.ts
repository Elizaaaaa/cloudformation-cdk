import * as cw from '@aws-cdk/aws-cloudwatch';
import { Construct } from '@aws-cdk/core';

export class CutTTAction implements cw.IAlarmAction {
  private readonly alarmActionArn: string;

  constructor() {
  this.alarmActionArn = "arn:aws:cloudwatch::cwa-internal:ticket:5:AWS:DeepEngine:Model+Parallelism:AWS+Model+Parallelism:";
  }

  bind(scope: Construct, alarm: cw.IAlarm): cw.AlarmActionConfig {
    return {
      alarmActionArn: this.alarmActionArn,
    };
  }