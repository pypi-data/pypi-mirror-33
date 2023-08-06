# -*- coding: utf8 -*-

import os
import config
import auth
import bucket
from xml_body import PartInfo
from progress import LimitedReader

def progress_func(transfered, total):
  pass
  #print('transfered:{0}, total:{1}'.format(transfered, total))

def prepare(access_key, secret_key, endpoint, is_cname, bucket_name):
  print('[prepare] ----> ')

  print('\taccess key={0}'.format(access_key))
  print('\tsecret key={0}'.format(secret_key))
  ath = auth.Authorize(access_key, secret_key)
  
  print('\tendpoint={0}'.format(endpoint))
  print('\tis CNAME={0}'.format(is_cname))

  print('\tbucket={0}'.format(bucket_name))
  
  return bucket.Bucket(ath, endpoint, bucket_name, is_cname)

def put_object_file(bkt, obj, file, limit=None):
  print('[put object from file] ----> ')

  print('\tobject={0}'.format(obj))
  print('\tfile={0}'.format(file))

  result = bkt.put_object_from_file(obj, file, progress_callback=progress_func, upload_speed_limited=limit)

  print('\tput object from file', result.status, result.request_id)
  return result

def put_object(bkt, obj, file, limit=None):
  print('[put object] ----> ')

  print('\tobject={0}'.format(obj))
  print('\tfile={0}'.format(file))

  with open(file, 'rb') as f:
    result = bkt.put_object(obj, f, progress_callback=progress_func, upload_speed_limited=limit)

  print('\tput object from file', result.status, result.request_id)
  return result

def generate_url(bkt, obj):
  print('[generate url] ----> ')
  sign_url = bkt.sign_url(obj, 60 * 60)
  print('\turl =', sign_url)

def multipart_upload(bkt, obj, file, limit=None):
  print('[multipart upload] ----> ')
  flen = os.path.getsize(file)
  with open(file, 'rb') as f:
    slice = (1024 * 1024) * 5

    times = flen // slice
    left = flen % slice

    print("\tfile://{0}'s length={1}, slice length={2}, times={3}, left={4}".format(file, flen, slice, times, left))

    result = bkt.init_multipart_upload(obj)
    uid = result.upload_id

    print('\tupload id={0}'.format(uid))

    parts = []
    number = 1
    while True:
      if times == 0:
        break
      
      reader = LimitedReader(f, slice)
      
      out = bkt.upload_part(obj, uid, number, reader, progress_callback=progress_func, upload_speed_limited=limit)
      part = PartInfo(number, out.etag)
      print('\tpart number={0}, ETag={1}'.format(number, out.etag))
      parts.append(part)

      number += 1
      times -= 1
    
    if left > 0:
      reader = LimitedReader(f, left)
      
      out = bkt.upload_part(obj, uid, number, reader, progress_callback=progress_func, upload_speed_limited=limit)
      part = PartInfo(number, out.etag)
      print('\tpart number={0}, ETag={1}'.format(number, out.etag))
      parts.append(part)

    result = bkt.complete_multipart_upload(obj, uid, parts)
  print('\tmultipart upload succeed...')


def list_bucket(access_key, secret_key, endpoint):
  authorization = auth.Authorize(access_key, secret_key)
  service = bucket.Service(authorization, endpoint)
  bucket_names = service.list_buckets(max_keys=10).buckets

  for bucket_name in bucket_names:
    print (bucket_name.name, bucket_name.creation_date)


def list_object(access_key, secret_key, endpoint, bucket_name):
  bkt = prepare(access_key, secret_key, endpoint, False, bucket_name)
  for item in bkt.list_objects().objects:
    print (item.key)


if __name__ == '__main__':
  conf = config.Config()

  access_key = conf.dict['access_key']
  secret_key = conf.dict['secret_key']
  endpoint = conf.dict['endpoint']
  is_cname = conf.dict['is_cname'] == 'true'
  bucket_name = conf.dict['bucket_name']

  bkt = prepare(access_key, secret_key, endpoint, is_cname, bucket_name)

  obj = conf.dict['object']
  file = conf.dict['file']
  try:
    limit = int(conf.dict['send_speed'])
  except:
    limit = 0
  
  print('\t speed limited={0}'.format(limit))
  put_object(bkt, obj, file)
  multipart_upload(bkt, obj, file, limit)

  generate_url(bkt, obj)

  list_bucket(access_key, secret_key, endpoint)

  list_object(access_key, secret_key, endpoint, "testing")
