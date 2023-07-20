from constants import readS3ConfigDataFromS3

readS3ConfFilesData = readS3ConfigDataFromS3()
AWS_AZ = readS3ConfFilesData['s3_bucket_region']
AWS_AZ_BACKUP = readS3ConfFilesData['s3_bucket_backup_region']
OUTPUT_S3_BUCKET = readS3ConfFilesData['s3_output_bucket']
OUTPUT_S3_BUCKET_BACKUP = readS3ConfFilesData['s3_backup_bucket']