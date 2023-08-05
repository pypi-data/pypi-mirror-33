# coding: utf-8
#  @author Raphael Reverdy <raphael.reverdy@akretion.com>
#          EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from datetime import datetime, timedelta


_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _dpd_get_shipping_date(self, package_id):
        """Estimate shipping date."""
        self.ensure_one()
        shipping_date = self.min_date
        if self.date_done:
            shipping_date = self.date_done

        shipping_date = datetime.strptime(
            shipping_date, DEFAULT_SERVER_DATETIME_FORMAT)

        tomorrow = datetime.now() + timedelta(1)
        if shipping_date < tomorrow:
            # don't send in the past
            shipping_date = tomorrow
        return shipping_date.strftime('%Y/%m/%d')
