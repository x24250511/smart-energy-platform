import boto3
import json
import os
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class CloudServiceManager:
    def __init__(self):
        self.use_aws = os.getenv('USE_REAL_AWS', 'False').lower() == 'true'
        
        if self.use_aws:
            self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
            self.s3_bucket = os.getenv('AWS_S3_BUCKET_NAME', '')
            self.dynamodb_table = os.getenv('AWS_DYNAMODB_TABLE', 'energy_users_backup')
            self.sns_topic_arn = os.getenv('AWS_SNS_TOPIC_ARN', '')
            self.lambda_function = os.getenv('AWS_LAMBDA_FUNCTION', 'EnergyCalculationFunction')
            
            try:
                self.s3 = boto3.client('s3', region_name=self.aws_region)
                self.dynamodb = boto3.client('dynamodb', region_name=self.aws_region)
                self.lambda_client = boto3.client('lambda', region_name=self.aws_region)
                self.sns = boto3.client('sns', region_name=self.aws_region)
                self.cloudwatch = boto3.client('cloudwatch', region_name=self.aws_region)
            except:
                self.use_aws = False
    
    def process_transaction_with_cloud(self, user, transaction_type, amount):
        if not self.use_aws:
            return {'success': True, 'message': 'AWS disabled', 'services_used': {}}
        
        results = {}
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace='SmartEnergyPlatform',
                MetricData=[{
                    'MetricName': f'Transaction_{transaction_type}',
                    'Value': amount,
                    'Timestamp': datetime.utcnow()
                }]
            )
            results['cloudwatch'] = True
        except:
            results['cloudwatch'] = False
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=self.lambda_function,
                InvocationType='RequestResponse',
                Payload=json.dumps({
                    'generated': float(user.generated),
                    'consumed': float(user.consumed),
                    'user_name': user.name,
                    'transaction_type': transaction_type,
                    'sns_topic_arn': self.sns_topic_arn
                })
            )
            results['lambda'] = True
        except:
            results['lambda'] = False
        
        try:
            self.dynamodb.put_item(
                TableName=self.dynamodb_table,
                Item={
                    'energy_number': {'S': user.energy_number},
                    'timestamp': {'S': datetime.now().isoformat()},
                    'name': {'S': user.name},
                    'generated': {'N': str(user.generated)},
                    'consumed': {'N': str(user.consumed)},
                    'credits': {'N': str(user.credits)},
                    'transaction_type': {'S': transaction_type},
                    'amount': {'N': str(amount)}
                }
            )
            results['dynamodb'] = True
        except:
            results['dynamodb'] = False
        
        try:
            if self.s3_bucket:
                pdf = self._generate_pdf(user, transaction_type, amount)
                filename = f"reports/{user.energy_number}_{transaction_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                self.s3.put_object(Bucket=self.s3_bucket, Key=filename, Body=pdf.getvalue(), ContentType='application/pdf')
                results['s3'] = True
            else:
                results['s3'] = False
        except:
            results['s3'] = False
        
        successful = sum(results.values())
        return {'success': True, 'message': f'{successful}/4 AWS services used', 'services_used': results}
    
    def _generate_pdf(self, user, transaction_type, amount):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, height - 100, "Smart Energy Platform")
        p.setFont("Helvetica", 12)
        p.drawString(100, height - 130, f"User: {user.name}")
        p.drawString(100, height - 150, f"Transaction: {transaction_type}")
        p.drawString(100, height - 170, f"Amount: {amount} kWh")
        p.drawString(100, height - 190, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

cloud_manager = CloudServiceManager()
