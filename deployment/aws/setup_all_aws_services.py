import boto3
import json
from io import BytesIO
import zipfile

def setup_dynamodb():
    dynamodb = boto3.client('dynamodb')
    
    try:
        dynamodb.create_table(
            TableName='energy_users_backup',
            KeySchema=[
                {'AttributeName': 'energy_number', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'energy_number', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("DynamoDB table created: energy_users_backup")
    except:
        print("DynamoDB table already exists")

def setup_s3():
    s3 = boto3.client('s3')
    bucket_name = 'smart-energy-platform-reports-2024'
    
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"S3 bucket created: {bucket_name}")
    except:
        print("S3 bucket already exists")

def setup_sns():
    sns = boto3.client('sns')
    
    response = sns.create_topic(Name='energy-platform-notifications')
    topic_arn = response['TopicArn']
    
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint='projectwebx11@gmail.com'
    )
    
    print(f"SNS topic created: {topic_arn}")
    print("Check email for confirmation")
    return topic_arn

def setup_lambda():
    lambda_client = boto3.client('lambda')
    sts = boto3.client('sts')
    
    account_id = sts.get_caller_identity()['Account']
    role_arn = f"arn:aws:iam::{account_id}:role/LabRole"
    
    code = '''
import json
import boto3

def lambda_handler(event, context):
    generated = float(event.get('generated', 0))
    consumed = float(event.get('consumed', 0))
    user_name = event.get('user_name', 'Unknown')
    transaction_type = event.get('transaction_type', 'calculation')
    sns_topic_arn = event.get('sns_topic_arn')
    
    surplus = max(0, generated - consumed)
    deficit = max(0, consumed - generated)
    efficiency = (generated / consumed * 100) if consumed > 0 else 0
    
    metrics = {
        'surplus_kwh': round(surplus, 2),
        'deficit_kwh': round(deficit, 2),
        'efficiency_percent': round(efficiency, 2)
    }
    
    if sns_topic_arn:
        try:
            sns = boto3.client('sns')
            message = f"User: {user_name}\\nTransaction: {transaction_type}\\nSurplus: {surplus} kWh"
            sns.publish(TopicArn=sns_topic_arn, Subject='Energy Transaction', Message=message)
        except:
            pass
    
    return {'statusCode': 200, 'body': json.dumps({'success': True, 'metrics': metrics})}
'''
    
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr('lambda_function.py', code)
    zip_buffer.seek(0)
    
    try:
        lambda_client.create_function(
            FunctionName='EnergyCalculationFunction',
            Runtime='python3.11',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_buffer.read()},
            Timeout=30,
            MemorySize=128
        )
        print("Lambda function created: EnergyCalculationFunction")
    except:
        print("Lambda function already exists")

if __name__ == '__main__':
    print("Setting up all AWS services...")
    setup_dynamodb()
    setup_s3()
    topic_arn = setup_sns()
    setup_lambda()
    print("\nSetup complete!")
    print(f"\nAdd to .env:")
    print(f"AWS_SNS_TOPIC_ARN={topic_arn}")
