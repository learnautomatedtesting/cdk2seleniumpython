#!/bin/bash
#chmod shell script 
#ECR_REPO_NAME_SEL_HUB="selenium-hub"
#ECR_REPO_NAME_CHROME="chrome"
#AWS_REGION="eu-west-2"
#AWS_ACCOUNT="" advice push this to an env account

source .env


aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.eu-west-2.amazonaws.com

if aws ecr describe-repositories --repository-names $ECR_REPO_NAME_SEL_HUB --region $AWS_REGION > /dev/null 2>&1; then
    echo "ECR repository $ECR_REPO_NAME_SEL_HUB already exists"
else
    aws ecr create-repository --repository-name $ECR_REPO_NAME_SEL_HUB  --region $AWS_REGION
    echo "ECR repository $ECR_REPO_NAME_SEL_HUB  created successfully"
fi


ECR_REPO_NAME="chrome"


if aws ecr describe-repositories --repository-names $ECR_REPO_NAME_CHROME --region $AWS_REGION > /dev/null 2>&1; then
    echo "ECR repository $ECR_REPO_NAME_CHROME already exists"
else
    aws ecr create-repository --repository-name $ECR_REPO_NAME_CHROME --region $AWS_REGION
    echo "ECR repository $ECR_REPO_NAME_CHROME created successfully"
fi

if aws ecr describe-repositories --repository-names $ECR_REPO_NAME_FIREFOX --region $AWS_REGION > /dev/null 2>&1; then
    echo "ECR repository $ECR_REPO_NAME_FIREFOX already exists"
else
    aws ecr create-repository --repository-name $ECR_REPO_NAME_FIREFOX --region $AWS_REGION
    echo "ECR repository $ECR_REPO_NAME_FIREFOX created successfully"
fi


docker build -t $ECR_REPO_NAME_SEL_HUB:latest -f lib/dockerfile/$ECR_REPO_NAME_SEL_HUB/Dockerfile .
docker tag $ECR_REPO_NAME_SEL_HUB:latest $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME_SEL_HUB:latest
docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME_SEL_HUB:latest  

docker build -t $ECR_REPO_NAME_CHROME:latest -f lib/dockerfile/$ECR_REPO_NAME_CHROME/Dockerfile .
docker tag $ECR_REPO_NAME_CHROME:latest $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME_CHROME:latest
docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME_CHROME:latest 

docker build -t $ECR_REPO_NAME_FIREFOX:latest -f lib/dockerfile/$ECR_REPO_NAME_FIREFOX/Dockerfile .
docker tag $ECR_REPO_NAME_FIREFOX:latest $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME_FIREFOX:latest
docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME_FIREFOX:latest 