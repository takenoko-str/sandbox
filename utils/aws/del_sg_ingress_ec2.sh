#!/bin/bash

PATTERN=xxx-*
PORT=22
IP_RANGE=32

aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=$PATTERN" \
  | jq -r ".Reservations[].Instances[].PublicIpAddress" \
  | sort \
  | uniq \
  | sed -e '$d' \
  | while read -r public_ip
  do
    echo "$public_ip"
    POLICY="[{
              \"IpProtocol\": \"tcp\", 
              \"FromPort\": $PORT, 
              \"ToPort\": $PORT, 
              \"IpRanges\": [{\"CidrIp\": \"$public_ip/$IP_RANGE\"}]
             }]"
	aws ec2 revoke-security-group-ingress \
	  --group-id ${GroupID} \
	  --ip-permissions "$POLICY"
  done