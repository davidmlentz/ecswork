I use these files according to the tutorial here: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-cli-tutorial-fargate.html

This is a guide to using ecs-cli to create an ECS cluster and task. Files here extend that to create a task that includes Datadog integration (metrics and logging).

ecs-cli/docker-compose.yml is where the task is defined. Once it's created (using ecs-cli) you can see the JSON in the ECS console.

Abbreviated from the tutorial, these are the commands I've used to get the task running from the CLI:

#
# 1. 
ecs-cli up --cluster-config tutorial --ecs-profile tutorial-profile
# The above command outputs a VPC ID to be used in the next command, 
# and 2 subnet IDs you'll need to use to update ecs-params.yml
#
# 2.
aws ec2 describe-security-groups --filters Name=vpc-id,Values=vpc-0abcd0123abcd0123 --region us-west-1
# NOTE the region specified in the above command. 
# It outputs some JSON which includes a security group ID you'll need for the next command.
#
# 3.
aws ec2 authorize-security-group-ingress --group-id sg-0abcd0123abcd0123 --protocol tcp --port 80 --cidr 0.0.0.0/0 --region us-west-1
#
# 4.
# Now update ecs-params.yml w/the subnet IDs and security group ID from the commands above:
vi ecs-params.yml 
#
# 5.
ecs-cli compose --project-name tutorial service up --create-log-groups --cluster-config tutorial --ecs-profile tutorial-profile
#
# 6.
# This next one will just show a status to confirm the previous command worked OK:
ecs-cli compose --project-name tutorial service ps --cluster-config tutorial --ecs-profile tutorial-profile
#
# 7.
# When you're done or need to start over, delete the task:
ecs-cli compose --project-name tutorial service down --cluster-config tutorial --ecs-profile tutorial-profile
#
# 8.
# Finally, if you're done, delete the cluster:
ecs-cli down --force --cluster-config tutorial --ecs-profile tutorial-profile
