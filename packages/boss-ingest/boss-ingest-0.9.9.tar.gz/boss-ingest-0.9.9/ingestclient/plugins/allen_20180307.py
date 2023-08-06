# Allen Institute's plugin to upload coregisterd data
# This plugin should work with the config files in configs/coregistered/ folder
from __future__ import absolute_import
import os
import logging

from .path import PathProcessor
from .tile import TileProcessor


class AiPathProcessor(PathProcessor):
    def setup(self, parameters):
        self.parameters = parameters

    def process(self, x_index, y_index, z_index, t_index=None):

        filename = "{}/{}/{}.{}".format(z_index, y_index, x_index, self.parameters["filetype"])
        full_path = os.path.join(self.parameters["root_dir"], filename)
        if os.path.isfile(full_path):
            return full_path
        else:
            return ''


class AiTileProcessor(TileProcessor):
    def __init__(self):
        """Constructor to add custom class var"""
        TileProcessor.__init__(self)
        self.data = None

    def setup(self, parameters):
        self.parameters = parameters

    def process(self, file_path, x_index, y_index, z_index, t_index=0):
        # if an image is missing, just send a blank one.
        if os.path.isfile(file_path):
            logger = logging.getLogger('ingest-client')
            logger.info("Sending: {}".format(file_path))
            return open(file_path, 'rb')
        else:
            logger = logging.getLogger('ingest-client')
            # logger.warning("Could not find path: {}".format(file_path))
            # TODO: figure out if I can return null here in order to avoid sending a blank png. How will an empty tile render using the API?
            return open('/allen/programs/celltypes/workgroups/em-connectomics/russelt/renderings/EM_Phase1/trakem2_PEA_fullstack_Trminusplus/1024x1024/empty.png', 'rb')