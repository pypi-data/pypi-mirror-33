import boto3

class S3():
  def __init__(self, bucket_name):
    self.s3           = boto3.resource('s3')
    self.s3client     = boto3.client('s3')
    self.bucket_name  = bucket_name
    self.bucket       = self.s3.Bucket(self.bucket_name)
    
  def get_subfolders(self, prefix='') :
    kwargs = {'Bucket': self.bucket_name , 'Delimiter' : '/' } 
    if isinstance(prefix, str): kwargs['Prefix'] = prefix 
   
    while True:
      resp = self.s3client.list_objects_v2(**kwargs)
      try:
        if len(resp['CommonPrefixes'])>0 :
          for f in resp['CommonPrefixes']:
            yield ( f['Prefix'])
      except KeyError:
        try:
          kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
          break     
        continue
      try:
        kwargs['ContinuationToken'] = resp['NextContinuationToken']
      except KeyError:
        break   
   
  def get_objects(self, prefix='', suffix='', recursive=True):
    if recursive :
      kwargs = {'Bucket': self.bucket_name}
    else:
      kwargs = {'Bucket': self.bucket_name, 'Delimiter' : '/' }
      
    if isinstance(prefix, str): kwargs['Prefix'] = prefix
    
    while True:
      resp = self.s3client.list_objects_v2(**kwargs)
      try:
        contents = resp['Contents']
      except KeyError:
        try:
          kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
          break      
        continue

      for obj in contents:
        key = obj['Key']
        if key.endswith(suffix): yield obj

      try:
        kwargs['ContinuationToken'] = resp['NextContinuationToken']
      except KeyError:
        break

  def get_keys(self, prefix='', suffix='', recursive=True):
    for obj in self.get_objects( prefix=prefix, suffix=suffix, recursive=recursive):
      yield obj['Key']

  def download_file(self, s3file, local_file):
    objs = self.get_objects(prefix=s3file)
    for obj in objs : print (obj)
    self.bucket.download_file(s3file, local_file)
      
if __name__ == "__main__":
  tafe_s3 = S3('product-cache-prd')
  s3list = tafe_s3.get_subfolders( prefix='product/', recursive=False)
  #tafe_s3 = S3('temp-files-api')
  #tafe_s3.download_file('00001Z', 'C:/temp/00001Z')
  
  for s in s3list :
    print (s)
  