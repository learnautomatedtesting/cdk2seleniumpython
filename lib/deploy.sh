#!/bin/bash

# Login to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin "282333594418.dkr.ecr.eu-west-2.amazonaws.com/cdk-hnb659fds-container-assets-282333594418-eu-west-2"

# Deploy the stack
cdk deploy