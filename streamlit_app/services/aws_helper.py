import boto3

def get_ssm_parameter(parameter_name, region_name='us-east-1'):
    ssm_client = boto3.client('ssm', region_name=region_name)

    try:
        response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        # Handle any other exceptions
        print(f"An unexpected error occurred: {e}")
        return None