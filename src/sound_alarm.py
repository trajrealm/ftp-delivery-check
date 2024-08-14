import configparser
import boto3


config = configparser.ConfigParser()
config.read('config/config.ini')

def sound_alarm(subj, msg):
    sns = boto3.client('sns', config['AWS_SNS']['aws_region'])
    topic_arn = config['AWS_SNS']['topic_arn']
    sns.publish(TopicArn='%s' % topic_arn, Message=msg, Subject=subj)
