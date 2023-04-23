from aws_cdk import (
        aws_ecr as ecr,
        aws_ecr_assets as ecr_assets,
        aws_ecs as ecs,
        aws_iam as iam,
        aws_ecs_patterns as ecs_patterns,
        aws_ec2 as ec2,
        aws_ecr as ecr,
        aws_elasticloadbalancingv2 as elbv2,
        aws_certificatemanager as acm,
        aws_route53 as route53,
        aws_route53_targets as targets, 
       
    
        
    
    )

import aws_cdk as cdk
# Add the following import statement
from aws_cdk.aws_elasticloadbalancingv2 import HealthCheck
from constructs import Construct
from aws_cdk import aws_logs as logs
from aws_cdk import aws_applicationautoscaling as appscaling
   
    

class SeleniumStack(cdk.Stack):

        def __init__(self, scope: Construct, id: str, **kwargs) -> None:
            super().__init__(scope, id, **kwargs)
            

            
            # Create a role
            my_role = iam.Role(
                self, "MyRole",
                assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
            )

            # Add the ECR policy to the role
            ecr_policy = iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryFullAccess")
            my_role.add_managed_policy(ecr_policy)

            try:
                # Check if ECR repositories exist
                chrome_repository = ecr.Repository.from_repository_name(self, "SeleniumChromeECRRepository", "chrome")
                firefox_repository = ecr.Repository.from_repository_name(self, "SeleniumFirefoxECRRepository", "firefox")
                hub_repository = ecr.Repository.from_repository_name(self, "SeleniumHubECRRepository", "selenium-hub")
            except Exception as e:
                print(f"Error: {e}")
                print("Failed to find one or more ECR repositories. Please ensure they exist before deployment.")
                return
        

                # Create a VPC for the Fargate service
            vpc = ec2.Vpc(
                self,
                "SeleniumVpc",
                max_azs=2,
            )

            # Create a Fargate cluster
            cluster = ecs.Cluster(
                self,
                "SeleniumCluster",
                vpc=vpc,
            )
            
             
            # Setup capacity providers and default strategy for cluster
            cfn_ecs_cluster = cluster.node.default_child
            cfn_ecs_cluster.add_override("Properties.CapacityProviders", ["FARGATE", "FARGATE_SPOT"])
            cfn_ecs_cluster.add_override("Properties.DefaultCapacityProviderStrategy", [
                {
                    "capacityProvider": "FARGATE",
                    "weight": 0,
                    "base": 0,
                },
                {
                    "capacityProvider": "FARGATE_SPOT",
                    "weight": 1,
                },
            ]
            )
            
            # Enable service discovery for the cluster
            namespace = cluster.add_default_cloud_map_namespace(
            name="selenium.local"
            )

            
         
           
            task_execution_role = iam.Role(
                    self,
                    "SeleniumFargateTaskExecutionRole",
                    assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                )
   

            # Add the ECR policy to the role
            ecr_policy = iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryFullAccess")
            task_execution_role.add_managed_policy(ecr_policy)

            # Add a custom policy to allow ecr:GetAuthorizationToken action
            task_execution_role.add_to_policy(
                iam.PolicyStatement(
                actions=["ecr:GetAuthorizationToken"],
                resources=["*"],
                )
            )
            
            task_execution_role.add_to_policy(
                 iam.PolicyStatement(
             actions=[
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams"
                ],
             resources=["arn:aws:logs:*:*:log-group:SeleniumTaskLogs:*"]
                )
            )
          
             # Request a certificate for the load balancer's default domain
           # certificate = acm.Certificate(self, "SeleniumHubCertificate", domain_name="*.elb.amazonaws.com", validation=acm.CertificateValidation.from_dns())

            
             # Set up a custom domain
            #domain_name = "learnautomatedtestingfargate.com"
            #hosted_zone = route53.HostedZone.from_lookup(self, "HostedZone", domain_name=domain_name)
            #certificate = acm.Certificate(self, "SeleniumHubCertificate", domain_name=f"selenium-hub.{domain_name}", validation=acm.CertificateValidation.from_dns(hosted_zone))
            # Create the Selenium Hub Fargate service
            self.create_selenium_hub_service(vpc,cluster, task_execution_role, hub_repository)
            
                
            node_security_group = ec2.SecurityGroup(
                self,
                "SeleniumNodeSecurityGroup",
                vpc=vpc,
                description="Allow inbound access to Selenium Node",
                allow_all_outbound=True,
            )
            
            
            node_security_group.add_ingress_rule(
                ec2.Peer.ipv4(vpc.vpc_cidr_block),
                ec2.Port.tcp(5555),
                "Allow inbound access to Selenium Node on port 5555",
            )
            
              
            try:
            # Try to import the existing LogGroup
                node_log_group = logs.LogGroup.from_log_group_name(self, "SeleniumNodeLogGroup","SeleniumNodeTaskLogs")
            
            except Exception as e:
                # If it doesn't exist, create a new one
                node_log_group = logs.LogGroup(self, "SeleniumNodeLogGroup", log_group_name="SeleniumNodeTaskLogs")
            # Create a log group for Selenium Node

            # Create the Chrome Node Fargate service
            chrome_service = self.create_selenium_node_service(vpc,"chrome", cluster, task_execution_role, chrome_repository,node_security_group,node_log_group)
             # Create the Firefox Node Fargate service
            firefox_service = self.create_selenium_node_service(vpc,"firefox", cluster, task_execution_role, firefox_repository,node_security_group,node_log_group)

            self.add_autoscaling_policy(chrome_service, "chrome")

            # Add autoscaling policy for firefox_service
            self.add_autoscaling_policy(firefox_service, "firefox")
        
        
        def create_selenium_hub_service(self, vpc: ec2.Vpc,cluster: ecs.Cluster, task_execution_role: iam.Role, hub_repository: ecr.Repository):
        # Create the Selenium Hub Fargate task definition
            hub_task_definition = ecs.FargateTaskDefinition(
                self, "SeleniumHubTask", memory_limit_mib=4096, cpu=1024,
                execution_role=task_execution_role,
                
            )
            
            
            hub_security_group = ec2.SecurityGroup(
                self,
                "SeleniumHubSecurityGroup",
                vpc=vpc,
                description="Allow inbound access to Selenium Hub",
                allow_all_outbound=True,
            )
            
            hub_security_group.add_ingress_rule(
                ec2.Peer.ipv4(vpc.vpc_cidr_block),
                ec2.Port.tcp(4442),
                "Allow inbound access to Selenium Hub on port 4442",
            )
            
            hub_security_group.add_ingress_rule(
                ec2.Peer.ipv4(vpc.vpc_cidr_block),
                ec2.Port.tcp(4443),
                "Allow inbound access to Selenium Hub on port 4443",
            )

            hub_security_group.add_ingress_rule(
                ec2.Peer.ipv4(vpc.vpc_cidr_block),
                ec2.Port.tcp(5900),
                "Allow inbound access to Selenium Hub VNC on port 5900",
            )
            
            # Create a log group for Selenium Hub
            
            try:
            # Try to import the existing LogGroup
                hub_log_group = logs.LogGroup.from_log_group_name(self, "SeleniumHubLogGroup","SeleniumHubTaskLogs")
            
            except Exception as e:
                # If it doesn't exist, create a new one
                 hub_log_group = logs.LogGroup(self, "SeleniumHubLogGroup", log_group_name="SeleniumHubTaskLogs")
         
            
           

            # Add the Selenium Hub container to the task definition
            hub_container = hub_task_definition.add_container(
            "selenium-hub",
            image=ecs.ContainerImage.from_registry(hub_repository.repository_uri),
            # Create a log group for Selenium Hub
            logging = ecs.LogDriver.aws_logs(
                    stream_prefix="SeleniumHub",
                    log_group=hub_log_group
                )
            )
            
         

           
           
            
        


            # Add port mappings for the Selenium Hub container
            hub_container.add_port_mappings(ecs.PortMapping(container_port=4444))
            hub_container.add_port_mappings(ecs.PortMapping(container_port=5900))


            hub_service = ecs_patterns.ApplicationLoadBalancedFargateService(
                self,
                "hub_service",
                cluster=cluster,
                task_definition=hub_task_definition,
                desired_count=1,
                protocol=elbv2.ApplicationProtocol.HTTP,  # Use HTTPS instead of HTTP
                public_load_balancer=True,
                security_groups=[hub_security_group],
                 # Add the certificate
                cloud_map_options=ecs.CloudMapOptions(
                name="selenium-hub",
                cloud_map_namespace=cluster.default_cloud_map_namespace,
                ),
                
            )
          
            
            hub_service.target_group.configure_health_check(
                path="/wd/hub/status",
                interval=cdk.Duration.seconds(30),
                timeout=cdk.Duration.seconds(5),
                healthy_http_codes="200",
                healthy_threshold_count=2,
                unhealthy_threshold_count=3,
            )








            

        
        
    
                
        def create_selenium_node_service(self,vpc:ec2.Vpc, browser: str, cluster: ecs.Cluster, task_execution_role: iam.Role, ecr_repository: ecr.Repository,node_security_group: ec2.SecurityGroup,node_log_group:logs.LogGroup):
            
            env_vars = {
                "SE_EVENT_BUS_HOST": "selenium-hub.selenium.local",
                "SE_EVENT_BUS_PUBLISH_PORT": "4442",
                "SE_EVENT_BUS_SUBSCRIBE_PORT": "4443",
            }
            
           
        
          
            


            task_definition = ecs.FargateTaskDefinition(
                self, f"Selenium{browser.title()}Task", memory_limit_mib=4096, cpu=1024,
                execution_role=task_execution_role,
               
            )

            container = task_definition.add_container(
                browser,
                image=ecs.ContainerImage.from_registry(ecr_repository.repository_uri),
                environment=env_vars,
                logging=ecs.LogDriver.aws_logs(
                        stream_prefix=f"Selenium{browser.title()}",
                        log_group=node_log_group
                 )
            )
            

            container.add_port_mappings(ecs.PortMapping(container_port=4444))

            service = ecs.FargateService(
                self,
                f"{browser}_service",
                cluster=cluster,
                task_definition=task_definition,
                desired_count=2,
                security_groups=[node_security_group],
                cloud_map_options=ecs.CloudMapOptions(
                    name=browser,
                    cloud_map_namespace=cluster.default_cloud_map_namespace,
                ),
            )
            
            # Add autoscaling policy for chrome_service
            return service 
  

        def add_autoscaling_policy(self, service: ecs.FargateService, browser: str):
            scaling = service.auto_scale_task_count(
                min_capacity=1,
                max_capacity=10,
            )

            scaling.scale_on_cpu_utilization(
                f"{browser}_cpu_scaling",
                target_utilization_percent=80,
                scale_in_cooldown=cdk.Duration.seconds(60),
                scale_out_cooldown=cdk.Duration.seconds(60),
             )  

            scaling.scale_on_memory_utilization(
            f"{browser}_memory_scaling",
            target_utilization_percent=80,
            scale_in_cooldown=cdk.Duration.seconds(60),
            scale_out_cooldown=cdk.Duration.seconds(60),
        )

            
            








