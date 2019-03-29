from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
   
    @api.multi
    def _action_launch_procurement_rule(self):
        res = super(SaleOrderLine, self)._action_launch_procurement_rule()
        orders = list(set(x.order_id for x in self))
        for order in orders:
            reassign = order.picking_ids.filtered(lambda x: x.state=='confirmed' or (x.state in ['waiting', 'assigned'] and not x.printed))
            if reassign:
                reassign.do_unreserve()
                reassign.action_assign()
        #Get all mo's and call action_assign on them
        for order_line in self:
            #mos=self.env['mrp.production']
            for schedule_line in order_line.schedule_lines:
                if schedule_line.state=='release':
                    i=0
                    #mos=schedule_line.mo_lines
                    while i < len(schedule_line.mo_lines):
                        for mo in schedule_line.mo_lines:
                            print("Runnning action assign")
                            if mo.procure_flag == False:
                                mo.action_assign()
                                mo.procure_flag=True
                                i+=1
                            print("Done Running Action Assign")
                schedule_line.write({
                    'state':'close'
                })
        return res