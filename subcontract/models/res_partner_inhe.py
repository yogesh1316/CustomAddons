
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import itertools
from operator import itemgetter
import datetime
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"


    #subcontract = fields.Boolean(string='Is a Subcontract', help="Check this box if this contact is a Subcontractor")
    
