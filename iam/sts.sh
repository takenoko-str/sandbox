#!/bin/bash

ROLE_NAME=$1

# AWS ACCOUNT IDを出力する方法
aws sts get-caller-identity --query 'Account' --output text

aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text

S3_BUCKET_NAME="codepipeline-${AWS_DEFAULT_REGION}-${AWS_ID}"