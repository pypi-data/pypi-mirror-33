# -*- coding: utf8 -*-

# xml body for request or response.

import re

from lxml import etree

from .result import InitMultipartUpload
from .portable import unicode_string, to_string, urlunquote
from .common import iso8601_to_unixtime, SimplifiedBucketInfo, SimplifiedObjectInfo


utf8_parser = etree.XMLParser(encoding='utf-8')


def _find_tag(parent, path):
    child = parent.find(path, parent.nsmap)
    if child is None:
        raise RuntimeError("parse xml: " + path + " could not be found under " + parent.tag)

    if child.text is None:
        return ''

    return to_string(child.text)


def _find_object(parent, path, url_encoded):
    name = _find_tag(parent, path)
    if url_encoded:
        return urlunquote(name)
    else:
        return name


class Parser(object):
    def __init__(self, resp):
        self.resp = resp
        self.body = resp.read()
        self.root = etree.fromstring(self.body)
        self.xml_namespaces = self.root.nsmap
    
    def init_multipart_upload(self):
        result = InitMultipartUpload(self.resp)
        result.upload_id = to_string(self.root.find('UploadId', self.xml_namespaces).text)

        return result


def _add_text_child(parent, tag, text):
    etree.SubElement(parent, tag).text = unicode_string(text)


def _xml_to_string(root):
    return etree.tostring(root, encoding='utf-8')


class PartInfo(object):
    """表示分片信息的文件。

    该文件既用于 :func:`list_parts <dawn.Bucket.list_parts>` 的输出，也用于 :func:`complete_multipart_upload
    <dawn.Bucket.complete_multipart_upload>` 的输入。

    :param int part_number: 分片号
    :param str etag: 分片的ETag
    """
    def __init__(self, part_number, etag):
        self.part_number = part_number
        self.etag = etag


class Maker(object):
    def __init__(self):
        pass

    def complete_upload_request(self, parts):
        root = etree.Element('CompleteMultipartUpload')
        for p in parts:
            node = etree.SubElement(root, 'Part')
            _add_text_child(node, 'PartNumber', str(p.part_number))
            _add_text_child(node, 'ETag', '"{0}"'.format(p.etag))
        
        return _xml_to_string(root)


def parse_list_buckets(result, body):
    root = etree.fromstring(body)

    if root.find('IsTruncated') is None:
        result.is_truncated = False
    else:
        result.is_truncated = root.find('IsTruncated', root.nsmap)

    if result.is_truncated:
        result.next_marker = root.find('NextMarker', root.nsmap)

    for bucket_node in root.findall('Buckets/Bucket', root.nsmap):
        result.buckets.append(SimplifiedBucketInfo(
            name=bucket_node.find('Name', bucket_node.nsmap).text,
            creation_date=iso8601_to_unixtime(bucket_node.find('CreationDate', bucket_node.nsmap).text)
        ))


def _is_url_encoding(root):
    node = root.find('EncodingType', root.nsmap)
    if node is not None and to_string(node.text) == 'url':
        return True
    else:
        return False


def parse_list_objects(result, body):
    root = etree.fromstring(body)

    url_encoded = _is_url_encoding(root)

    for contents_node in root.findall('Contents', root.nsmap):
        result.objects.append(SimplifiedObjectInfo(
            _find_object(contents_node, 'Key', url_encoded),
            iso8601_to_unixtime(_find_tag(contents_node, 'LastModified')),
            _find_tag(contents_node, 'ETag').strip('"'),
            int(_find_tag(contents_node, 'Size')),
            _find_tag(contents_node, 'StorageClass')
        ))

    for prefix_node in root.findall('CommonPrefixes', root.nsmap):
        result.prefixes.append(_find_object(prefix_node, 'Prefix', url_encoded))

    return result

