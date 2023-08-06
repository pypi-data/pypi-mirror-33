# Allen Institute's plugin to upload coregisterd data
# This plugin should work with the config files in configs/coregistered/ folder
from __future__ import absolute_import
import os
import logging
import boto3
from botocore.exceptions import ClientError

from .path import PathProcessor
from .tile import TileProcessor
from io import BytesIO
import six
import numpy as np
from PIL import Image


class AiPathProcessor(PathProcessor):
    def setup(self, parameters):
        self.parameters = parameters

    def process(self, x_index, y_index, z_index, t_index=None):

        filename = "{}/{}/{}.{}".format(z_index, y_index, x_index, self.parameters["filetype"])
        full_path = os.path.join(self.parameters["root_dir"], filename)
        return full_path
        # if os.path.isfile(full_path):
        #     return full_path
        # else:
        #     return ''


class AiS3TileProcessor(TileProcessor):
    def __init__(self):
        """Constructor to add custom class var"""
        TileProcessor.__init__(self)
        self.data = None
        self.logger = logging.getLogger('ingest-client')

    def setup(self, parameters):
        self.parameters = parameters
        self.client = boto3.client("s3")

    def process(self, file_path, x_index, y_index, z_index, t_index=0):
        try:
            resp = self.client.get_object(Bucket=self.parameters['bucket'],
                                          Key=file_path)
            if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
                self.logger.error('HTTPStatusCode: {} on {}'.format(resp['ResponseMetadata']['HTTPStatusCode'],
                                                                    file_path))
                return None
            else:
                #return resp['Body']
                #data = np.load(BytesIO(resp['Body'].read()))
                # Save sub-img to png and return handle
                # upload_img = Image.fromarray(np.squeeze(data))
                # output = six.BytesIO()
                #upload_img.save(output, format="PNG")

                data = BytesIO(resp['Body'].read())
                # Send handle back
                return data
        except ClientError as ex:
            if ex.response['Error']['Code'] == 'NoSuchKey':
                self.logger.warning('No object found: {}'.format(file_path))
                return open('/ingest-client/black-1024x1024.png', 'rb')
            elif ex.response['Error']['Code'] == 'NoSuchBucket':
                print('No such bucket found')
                self.logger.error('No bucket found: {}'.format(self.parameters['bucket']))
                raise ex
            else:
                raise ex

        # # if an image is missing, just send a blank one.
        # if os.path.isfile(file_path):
        #     logger = logging.getLogger('ingest-client')
        #     logger.info("Sending: {}".format(file_path))
        #     return open(file_path, 'rb')
        # else:
        #     logger = logging.getLogger('ingest-client')
        #     # logger.warning("Could not find path: {}".format(file_path))
        #     # TODO: figure out if I can return null here in order to avoid sending a blank png. How will an empty tile render using the API?
        #     return open('/allen/programs/celltypes/workgroups/em-connectomics/russelt/renderings/EM_Phase1/trakem2_PEA_fullstack_Trminusplus/1024x1024/empty.png', 'rb')