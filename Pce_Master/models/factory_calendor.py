from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from datetime import datetime,timedelta
import calendar
import time
import json
import time
from time import gmtime, strftime


class factory_calendor(models.Model):
    _name='factory.calendor'
    #year=fields.Char(string='Year',required=True,)
    year= fields.Selection([(num, str(num)) for num in range(2000, (datetime.now().year)+50 )],'Year')
    shift = fields.Many2one('resource.calendar',string='Work Center', required=True,)
    weak_no=fields.Char()
    flag=fields.Integer()
    seq_no=fields.Integer()
    company_id=fields.Integer()
    ydate=fields.Date()
    #####Commented added
    @api.multi
    def get_year_fact(self):

        ##   Developed by Hrishikesh Kulkanri  
        #### reset factory calendor data year and shift id wise

        self.env.cr.execute("delete from factory_calendor where year=%s and shift=%s",(self.year,self.shift.id,))
        factory_calendor_obj = self.env['factory.calendor']
        flg='0'
        thisdict = { }
        dictthis={ }
        fact_line={ }
        a1=''
        b1=''

        ## Get records from calendar attendance and calendar leaves
        resource_calendar_data_obj = self.env['resource.calendar.attendance']        
        ## Get year of First date of january and end date december
        a1 = str(datetime(self.year, 1, 1))
        b1 = str(datetime(self.year, 12, 31))      
       
        a2=datetime.strptime(a1, "%Y-%m-%d %H:%M:%S")
        a12 = a2.strftime("%d-%m-%Y")
        b2=datetime.strptime(b1, "%Y-%m-%d %H:%M:%S")
        b12 = b2.strftime("%d-%m-%Y")
        start = datetime.strptime(a12, '%d-%m-%Y')
        end = datetime.strptime(b12, '%d-%m-%Y')

        ## get two date between dates
        date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days+1)]
        i=1
        j=0
        cidata=resource_calendar_data_obj.search([('calendar_id','=',self.shift.id)])
        weekd=0
        lineweekd=0
        holiday=''
        for date in date_generated:
            weekd=date.weekday()
            ydate=date.strftime("%d-%m-%Y")
            for line in cidata:
                lineweekd=int(line.dayofweek)
                if weekd==lineweekd:
                    flg='1'
                    break;
            #add data to list variable 
            thisdict[i]={'date':ydate,'flag':flg,'seq':i}
            flg='0'
            i=i+1
        k=1
        lseq_no=0

        for fline in thisdict.items():                    
            start12= datetime.strptime(fline[1]['date'], "%d-%m-%Y").strftime("%Y-%m-%d")
            lweak_no= datetime.strptime(fline[1]['date'], "%d-%m-%Y").strftime("%V")
            if fline[1]['flag'] =='0':
                lseq_no=0
            elif fline[1]['flag'] =='1':        
                lseq_no=k     
                k=k+1
            fact_line = {
                    'ydate':start12,
                    'year':self.year,
                    'shift': self.shift.id,
                    'weak_no':lweak_no,
                    'flag': fline[1]['flag'],
                    'seq_no': lseq_no,
                    'company_id': self.env.user.company_id.id,
                }
            #Save the record to the factory_calendor table
            # self._cr.execute("select distinct count(*)/5 as count from resource_calendar_attendance where calendar_id=%s",(self.shift.id,))
            # #shift_list= self.env.cr.fetchall()
            # self.deadline = self.env.cr.fetchone()[0]
            # for counter in  range(0,self.deadline):     
            obj_gn=factory_calendor_obj.create(fact_line)
            #     print('print',counter+1)
        
        self._cr.execute("select date_from,date_to from resource_calendar_leaves where date_part('year', date_from)=%s\
        and calendar_id=%s",(self.year,self.shift.id))
        holiday= self.env.cr.fetchall()
        for hline in holiday:
            datestr=datetime.strptime(hline[0], "%Y-%m-%d %H:%M:%S")
            s1date = datestr.strftime("%d-%m-%Y")
            datestr1=datetime.strptime(hline[1], "%Y-%m-%d %H:%M:%S")
            s2date = datestr1.strftime("%d-%m-%Y")
            date_generated = [datestr + timedelta(days=x) for x in range(0, (datestr1-datestr).days+1)]
            for date in date_generated:
                sdate3=date.strftime("%Y-%m-%d")   
                self._cr.execute("select id,year,weak_no,ydate,shift from factory_calendor where ydate=%s and shift=%s",(sdate3,self.shift.id))
                temp= self.env.cr.fetchall()
                for l in temp:
                    if sdate3==l[3]:
                        self.env.cr.execute("update factory_calendor set flag=%s where ydate=%s and shift=%s",('0',sdate3,self.shift.id))
                    else:
                        print('Record Found Not')
        ##Update the sequence the factory_calendor
        self._cr.execute("select flag,ydate from factory_calendor where year=%s and shift=%s order by ydate",(self.year,self.shift.id))
        temp1= self.env.cr.fetchall()
        t1=1
        for l1 in temp1:
            if str(l1[0])=='0':
                self.env.cr.execute("update factory_calendor set seq_no=%s where ydate=%s and shift=%s",('0',l1[1],self.shift.id))
            else:
                self.env.cr.execute("update factory_calendor set seq_no=%s where ydate=%s and shift=%s",(t1,l1[1],self.shift.id))
                t1=t1+1