
# References:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html

import boto3
import traceback
import logging

#logging setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client('ec2')

def lambda_handler(event, context):

    try:
        start_stop_ec2_instances(event, context)
        

        
    except Exception as e:
            displayException(e)
            traceback.print_exc()
            
def start_stop_ec2_instances(event, context):
    
    # Get action parameter from event
    action = event.get('action')
    
    if action is None:
        action = ''

    # Check action
    if action.lower() not in ['start', 'stop']:
        print (" Please pass start or stop request for this to work.")
    else:
        # Get ec2 instances which match filter conditions
        filtered_ec2 = ec2.describe_instances(
            Filters=[
                {'Name': 'tag-key', 'Values': ['dev']},
                {'Name': 'tag-value', 'Values': ['true']},
                {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
            ]
        ).get(
            'Reservations', []
        )
    
        # Convert array of array to a flat array
        instances_ec2 = sum(
            [
                [i for i in r['Instances']]
                for r in filtered_ec2
            ], [])
    
        print ("Found " + str(len(instances_ec2)) + " EC2 instances that can be started or stopped")
    
        # Loop through instances
        for instance_ec2 in instances_ec2:

            try:
                instance_id = instance_ec2['InstanceId']

                # Get ec2 instance name tag
                for tag in instance_ec2['Tags']:
                    if tag['Key'] == 'dev':
                        instance_name = tag['Value']
                        print ("instance_name: " + instance_name + " instance_id: " + instance_id)
                        continue
                    
                # Get ec2 instance current status
                instance_state = instance_ec2['State']['Name']
                print ("Current instance_state: %s" % instance_state)
                
                # Start or stop ec2 instance
                if instance_state == 'running' and action == 'stop':
                    ec2.stop_instances(
                        InstanceIds=[
                            instance_id
                            ],
                
                        )
                    print ("Instance %s comes to stop" % instance_id)
                    
                elif instance_state == 'stopped' and action == 'start':
                    ec2.start_instances(
                        InstanceIds=[
                            instance_id
                            ],
       
                        )
                    print ("Instance %s comes to start" % instance_id)
                    
                else:
                    print ("Instance %s(%s) status is invalid for start or stop" % (instance_id, instance_name))
                
            except Exception as e:
                displayException(e)
               

def displayException(exception):
    exception_type = exception.__class__.__name__ 
    exception_message = str(exception) 

    print("Exception type: %s; Exception message: %s;" % (exception_type, exception_message))
