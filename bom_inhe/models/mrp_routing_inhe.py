from odoo import api, fields, models, _
from decimal import Decimal

# create_by | create_date | update_by | update_date
# Ganesh      15/10/2018    
# Info : Inherite mrp.routing.workcenter for cutomise 

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    # Added New Field 
    setup_time = fields.Float(string='Setup time', default=60, help="Setup Time required for Operation")
    operation_time = fields.Float(string='Operation time', default=60, help="Time required to perform Operation")
    transfer_time = fields.Float(string='Transfer time', default=1, help="Transfer Time for Operation")

    cum_setup_time = fields.Float(string='Cumulative setup time', help="Setup time required for Operation")
    cum_ope_time = fields.Float(string='Cumulative operation time', help="Time required to perform Operation")
    cum_tran_time = fields.Float(string='Cumulative transfer time', help="Setup time required for Operation")

    # Calculate Cumulative Time on Create
    @api.model
    def create(self, vals):      
        mrw_id = super(MrpRoutingWorkcenter, self).create(vals)
        #print('values-----',mrw_id.routing_id.id)
        self._cr.execute("select id  from mrp_routing_workcenter where routing_id=%s order by id",(mrw_id.routing_id.id,))
        id_desc= self.env.cr.fetchall()
        #print('id_desc',id_desc)
        for ids in id_desc:
            #print('id--',ids)
            self._cr.execute("select sum(setup_time) as s,sum(operation_time) as o,sum(transfer_time) as t  \
            from mrp_routing_workcenter where routing_id=%s and id <=%s",(mrw_id.routing_id.id,ids))
            tempdata=self.env.cr.fetchall() 
            #print('data',tempdata[0],ids)
            for val in tempdata:
                self._cr.execute("update mrp_routing_workcenter set cum_setup_time=%s,cum_ope_time=%s,cum_tran_time=%s where id=%s",(val[0],val[1],val[2],ids))
    
    # Calculate Cumulative Time on Update
    @api.model
    def write(self, vals):  
        #print('ids',self.routing_id.id)
        mrw_id = super(MrpRoutingWorkcenter, self).write(vals)
        #print('values-----',mrw_id.routing_id.id)
        self._cr.execute("select id  from mrp_routing_workcenter where routing_id=%s order by id",(self.routing_id.id,))
        id_desc= self.env.cr.fetchall()
        print('id_desc',id_desc)
        for ids in id_desc:
            #print('id--',ids)
            self._cr.execute("select sum(setup_time) as s,sum(operation_time) as o,sum(transfer_time) as t  \
            from mrp_routing_workcenter where routing_id=%s and id <=%s",(self.routing_id.id,ids))
            tempdata=self.env.cr.fetchall() 
            #print('data',tempdata[0],ids)
            for val in tempdata:
                self._cr.execute("update mrp_routing_workcenter set cum_setup_time=%s,cum_ope_time=%s,cum_tran_time=%s where id=%s",(val[0],val[1],val[2],ids))
    
    # Calculate time_cycle_manual on setup_time,operation_time and transfer_time
    @api.multi
    @api.onchange('setup_time','operation_time','transfer_time')
    def default_duration_cal(self):
        st = 0.00
        ot = 0.00
        dd = 0.00
        tt = 0.00  
        flagdecima=0.00      
        mins=0.00
        hrs=0
        tt=self.transfer_time
        hrs,mins=divmod(tt,1)        
        flagdecima= mins*100               
        st = self.setup_time
        ot = self.operation_time
        tt = ((hrs * 60)+round(flagdecima,2))       
        print('tt',tt,st,ot)
        dd = st + ot + tt
        print(dd)
        self.time_cycle_manual = dd
    
    



   