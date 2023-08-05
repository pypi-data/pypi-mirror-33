# -*- coding: utf-8 -*-
from generic_erp.document.document import Document


class StockPicking(Document):

    def __init__(self, partner):
        super(StockPicking, self).__init__(partner)
        self.picking_lines = []
