# -*- encoding: utf-8 -*-
from pyf.transport.packets import Packet
from pyf.station.client import StationClient

from pyf.station.utils import base64encoder
from pyf.station.utils import base64decoder
from pyf.station.utils import file_to_packets
from pyf.station.utils import handle_data_packet

import json
import logging


class RenderClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.authtkt = ''

    def login(self, user_name, password):
        self.authtkt = ''

    def render(
        self, input_filename, output_filename,
        target_format='pdf', source_format='odt', pdf_options=None
    ):
        client = StationClient(self.host, self.port, waits_for_success=True)
        flow = base64encoder(file_to_packets(open(input_filename, 'rb')))
        if pdf_options:
            pdf_options = json.dumps(pdf_options)

        values = base64decoder(
            client.call(
                flow,
                header=dict(
                    authtkt=self.authtkt,
                    action='render',
                    target_format=target_format,
                    source_format=source_format,
                    pdf_options=pdf_options,
                ),
            )
        )

        output_file = None
        for value in values:

            if isinstance(value, Packet) and \
               value.type == 'appinfo' and \
               value.key == 'render_status':
                if value.value == 'ok':
                    logging.info(
                        "Rendering ok: %s. Fetching file." % input_filename
                    )
                else:
                    raise ValueError("Render failed, no reason given.")

            if isinstance(value, Packet) and value.type == 'datatransfer':
                if output_file is None:
                    output_file = open(output_filename, 'wb')

                finished = handle_data_packet(value, output_file)

                if finished:
                    output_file.close()
                    logging.info("File %s fetched" % output_filename)
