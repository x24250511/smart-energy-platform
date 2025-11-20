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

def setup_cloudwatch_dashboard():
    cloudwatch = boto3.client('cloudwatch')
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0,
                "y": 0,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["SmartEnergyPlatform", "Transaction_buyback", {"stat": "Sum", "label": "Buyback Transactions"}],
                        [".", "Transaction_loan", {"stat": "Sum", "label": "Loan Transactions"}],
                        [".", "Transaction_donation", {"stat": "Sum", "label": "Donation Transactions"}]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "Energy Transactions by Type",
                    "period": 300,
                    "yAxis": {
                        "left": {
                            "label": "kWh"
                        }
                    }
                }
            },
            {
                "type": "metric",
                "x": 12,
                "y": 0,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["SmartEnergyPlatform", "Transaction_buyback", {"stat": "Sum"}],
                        [".", "Transaction_loan", {"stat": "Sum"}],
                        [".", "Transaction_donation", {"stat": "Sum"}]
                    ],
                    "view": "singleValue",
                    "region": "us-east-1",
                    "title": "Total Energy Traded (kWh)",
                    "period": 86400
                }
            },
            {
                "type": "metric",
                "x": 0,
                "y": 6,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["SmartEnergyPlatform", "Transaction_buyback", {"stat": "SampleCount", "label": "Buyback Count"}],
                        [".", "Transaction_loan", {"stat": "SampleCount", "label": "Loan Count"}],
                        [".", "Transaction_donation", {"stat": "SampleCount", "label": "Donation Count"}]
                    ],
                    "view": "pie",
                    "region": "us-east-1",
                    "title": "Transaction Distribution",
                    "period": 86400
                }
            },
            {
                "type": "metric",
                "x": 12,
                "y": 6,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["SmartEnergyPlatform", "Transaction_buyback", {"stat": "Average"}],
                        [".", "Transaction_loan", {"stat": "Average"}],
                        [".", "Transaction_donation", {"stat": "Average"}]
                    ],
                    "view": "timeSeries",
                    "stacked": True,
                    "region": "us-east-1",
                    "title": "Average Transaction Size",
                    "period": 3600,
                    "yAxis": {
                        "left": {
                            "label": "kWh"
                        }
                    }
                }
            },
            {
                "type": "metric",
                "x": 0,
                "y": 12,
                "width": 24,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/Lambda", "Invocations", {"stat": "Sum", "label": "Lambda Invocations"}],
                        [".", "Errors", {"stat": "Sum", "label": "Lambda Errors"}],
                        [".", "Duration", {"stat": "Average", "label": "Avg Duration (ms)"}]
                    ],
                    "view": "timeSeries",
                    "region": "us-east-1",
                    "title": "Lambda Performance Metrics",
                    "period": 300
                }
            }
        ]
    }
    
    try:
        cloudwatch.put_dashboard(
            DashboardName='SmartEnergyPlatform',
            DashboardBody=json.dumps(dashboard_body)
        )
        print("CloudWatch Dashboard created: SmartEnergyPlatform")
        print("View at: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=SmartEnergyPlatform")
    except Exception as e:
        print(f"CloudWatch Dashboard error: {e}")

if __name__ == '__main__':
    print("Setting up all 5 AWS services...")
    print("=" * 60)
    
    print("\n1. Setting up DynamoDB...")
    setup_dynamodb()
    
    print("\n2. Setting up S3...")
    setup_s3()
    
    print("\n3. Setting up SNS...")
    topic_arn = setup_sns()
    
    print("\n4. Setting up Lambda...")
    setup_lambda()
    
    print("\n5. Setting up CloudWatch Dashboard...")
    setup_cloudwatch_dashboard()
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("\nAdd to .env:")
    print(f"AWS_SNS_TOPIC_ARN={topic_arn}")
    print("\nDashboard Features:")
    print("- Transaction trends over time")
    print("- Total energy traded")
    print("- Transaction distribution")
    print("- Average transaction sizes")
    print("- Lambda performance metrics")
