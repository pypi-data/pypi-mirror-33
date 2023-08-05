# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateTransition, StateView, Button, StateAction
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id, Or
from trytond.transaction import Transaction
from datetime import datetime, timedelta
from trytond.modules.employee_timetracking.period import WF_PERIOD_CREATED


__all__ = ['PeriodAttendanceWizard', 'PeriodAttendanceWizardStart']
__metaclass__ = PoolMeta


CURRSTAT_ABSENT = 'a'
CURRSTAT_PRESENT = 'p'
CURRSTAT_SITEWORK = 's'
CURRSTAT_ACTIVE = 'k'
sel_currstate = [
        (CURRSTAT_ABSENT, u'Absent'),
        (CURRSTAT_PRESENT, u'Present'),
        (CURRSTAT_SITEWORK, u'on site work'),
        (CURRSTAT_ACTIVE, u'Active')
    ]

class PeriodAttendanceWizardStart(ModelView):
    'Enter attendance - start'
    __name__ = 'employee_timetracking.wizperiod_attendance.start'

    company = fields.Many2One(string="Company", model_name='company.company', 
                readonly=True, depends=['employee'])
    employee = fields.Many2One(string="Employee", model_name='company.employee',
                states={
                    'readonly': ~Or(
                            Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                            Id('employee_timetracking', 'group_worktime_edit').in_(Eval('context', {}).get('groups', [])),
                        )
                }, 
                domain=[
                    ('company', '=', Eval('context', {}).get('company', None)),
                    ('tariff', '!=', None)
                ])
    currstate = fields.Selection(string=u'Current State', readonly=True, 
                    selection=sel_currstate)
    currtype = fields.Char(string=u'Type of Presence', readonly=True)
    currstart = fields.DateTime(string=u'Start', readonly=True)
    currperiod = fields.Char(string=u'Time period', readonly=True)

    @classmethod
    def __setup__(cls):
        super(PeriodAttendanceWizardStart, cls).__setup__()
        cls._error_messages.update({
                'enterper_notariff': (u"Please assign a tariff to employee '%s' first."),
                })

    @fields.depends('company', 'employee','currstate', 'currstart', 'currperiod')
    def on_change_employee(self):
        """ update company
        """
        def set_current_info(self, startperiod):
            if startperiod.presence == self.employee.tariff.type_present:
                self.currstate = CURRSTAT_PRESENT
                self.currstart = startperiod.startpos
                self.currperiod = self.format_timedelta(self.get_delta(startperiod.startpos))
                self.currtype = startperiod.presence.name
            elif startperiod.presence == self.employee.tariff.type_sitework:
                self.currstate = CURRSTAT_SITEWORK
                self.currstart = startperiod.startpos
                self.currperiod = self.format_timedelta(self.get_delta(startperiod.startpos))
                self.currtype = startperiod.presence.name
            else :
                self.currstate = CURRSTAT_ACTIVE
                self.currstart = startperiod.startpos
                self.currperiod = self.format_timedelta(self.get_delta(startperiod.startpos))
                self.currtype = startperiod.presence.name
            
        if not isinstance(self.employee, type(None)):
            if isinstance(self.employee.tariff, type(None)):
                self.raise_user_error('enterper_notariff', (self.employee.party.rec_name))
                
            self.company = self.employee.company

            Period = Pool().get('employee_timetracking.period')
            # newest item by startpos
            s_lst = Period.search([('employee', '=', self.employee), ('startpos', '!=', None)], 
                        order=[('startpos', 'DESC')], limit=1)
            # newest item by endpos
            e_lst = Period.search([('employee', '=', self.employee), ('endpos', '!=', None)], 
                        order=[('endpos', 'DESC')], limit=1)

            self.currstart = None
            self.currperiod = ''
            self.currtype = ''
            if (len(s_lst) > 0) and (len(e_lst) > 0):
                if s_lst[0].id == e_lst[0].id:
                    self.currstate = CURRSTAT_ABSENT
                elif s_lst[0].startpos > e_lst[0].endpos:
                    # last item is 'begin'
                    set_current_info(self, s_lst[0])
                else :
                    self.currstate = CURRSTAT_ABSENT
            elif (len(s_lst) > 0) and (len(e_lst) == 0):
                set_current_info(self, s_lst[0])
            else :
                self.currstate = CURRSTAT_ABSENT
        else :
            self.currstart = None
            self.currperiod = None
            self.currtype = ''
            self.currstate = CURRSTAT_ABSENT

    def format_timedelta(self, tdelta):
        """ format
        """
        hours = tdelta.seconds // (60 * 60)
        minutes = (tdelta.seconds - hours * 60 *60) // 60
        t1 = '%d h, %02d m' % (hours, minutes)
        if tdelta.days > 0:
            return '%d d, %s' % (tdelta.days, t1)
        else :
            return t1

    def get_delta(self, startpos):
        """ get timedelta since start, round down to minute
        """
        sec1 = (datetime.now() - startpos).seconds
        sec1 = sec1 - sec1 % 60
        return timedelta(seconds=sec1, days=(datetime.now() - startpos).days)
        
# end PeriodAttendanceWizardStart


class PeriodAttendanceWizard(Wizard):
    'Enter attendance'
    __name__ = 'employee_timetracking.wizperiod_attendance'
    
    start_state = 'start'
    start = StateView(model_name='employee_timetracking.wizperiod_attendance.start', \
                view='employee_timetracking.attendance_wizard_start_form', \
                buttons=[Button(string=u'Cancel', state='end', icon='tryton-cancel'), 
                         Button(string=u'End site work', state='endsite', icon='tryton-save'),
                         Button(string=u'Start site work', state='startsite', icon='tryton-save'),
                         Button(string=u'Going', state='going', icon='tryton-save'),
                         Button(string=u'Coming', state='coming', icon='tryton-save')])
    coming = StateTransition()
    going = StateTransition()
    startsite = StateTransition()
    endsite = StateTransition()
    
    @classmethod
    def __setup__(cls):
        super(PeriodAttendanceWizard, cls).__setup__()
        cls._error_messages.update({
                'enterper_noemployee': (u"Please select an employee first."),
                'enterper_notariff': (u"Please assign a tariff to employee '%s' first."),
                })
    
    def default_start(self, fields):
        """ fill form
        """
        r1 = {}
        tr1 = Transaction()
        r1['employee'] = Transaction().context.get('employee', None)
        r1['currstate'] = CURRSTAT_PRESENT
        return r1

    def open_item(self, pres_type):
        """ open a item of type 'pres_type'
        """
        if isinstance(self.start.employee, type(None)):
            self.raise_user_error('enterper_noemployee')
        
        Period = Pool().get('employee_timetracking.period')
        
        # search possibly open item
        o_lst = Period.search([
                    ('employee', '=', self.start.employee),
                    ('presence', 'in', [self.start.employee.tariff.type_sitework, 
                                        self.start.employee.tariff.type_present]),
                ], order=[('startpos', 'DESC')], limit=1)

        if len(o_lst) > 0:
            if o_lst[0].state == WF_PERIOD_CREATED:
                # startpos not older than 12h
                if isinstance(o_lst[0].endpos, type(None)) and \
                    ((o_lst[0].startpos + timedelta(seconds=12*60*60)) > datetime.now()):
                    o_lst[0].endpos = datetime.now() - timedelta(seconds=5)
                    o_lst[0].save()
                    Period.wfexamine([o_lst[0]])    # wf-step

        pobj = Period(
                    employee=self.start.employee,
                    presence=pres_type,
                    startpos=datetime.now(),
                    endpos=None,
                    state=Period.default_state()
                )
        pobj.save()
    
    def close_item(self, pres_type):
        """ close a item of 'pres_type'
        """
        if isinstance(self.start.employee, type(None)):
            self.raise_user_error('enterper_noemployee')
            
        # find open item
        Period = Pool().get('employee_timetracking.period')
        p_lst = Period.search([
                    ('employee', '=', self.start.employee),
                    ('presence', 'in', [self.start.employee.tariff.type_sitework, 
                                        self.start.employee.tariff.type_present])
                ], order=[('write_date', 'DESC')], limit=1)

        if len(p_lst) > 0:
            # if newest item is of 'pres_type' and still open
            if (p_lst[0].presence == pres_type) and \
                (p_lst[0].state == WF_PERIOD_CREATED) and \
                (not isinstance(p_lst[0].startpos, type(None))) and \
                isinstance(p_lst[0].endpos, type(None)):
                p_lst[0].endpos = datetime.now()
                p_lst[0].save()
                Period.wfexamine([p_lst[0]])    # wf-step
        else :
            # no open item found- create one
            pobj = Period(
                        employee=self.start.employee,
                        presence=pres_type,
                        startpos=None,
                        endpos=datetime.now(),
                        state=Period.default_state()
                    )
            pobj.save()

    def transition_startsite(self):
        """ store start of 'site work'
        """
        if isinstance(self.start.employee, type(None)):
            self.raise_user_error('enterper_noemployee')
        if isinstance(self.start.employee.tariff, type(None)):
            self.raise_user_error('enterper_notariff', (self.start.employee.party.rec_name))
        self.open_item(self.start.employee.tariff.type_sitework)
        return 'end'

    def transition_endsite(self):
        """ store end of site work
        """
        if isinstance(self.start.employee, type(None)):
            self.raise_user_error('enterper_noemployee')
        if isinstance(self.start.employee.tariff, type(None)):
            self.raise_user_error('enterper_notariff', (self.start.employee.party.rec_name))
        self.close_item(self.start.employee.tariff.type_sitework)
        return 'end'

    def transition_going(self):
        """ store end of local work
        """
        if isinstance(self.start.employee, type(None)):
            self.raise_user_error('enterper_noemployee')
        if isinstance(self.start.employee.tariff, type(None)):
            self.raise_user_error('enterper_notariff', (self.start.employee.party.rec_name))
        self.close_item(self.start.employee.tariff.type_present)
        return 'end'

    def transition_coming(self):
        """ store start of local work
        """
        if isinstance(self.start.employee, type(None)):
            self.raise_user_error('enterper_noemployee')
        if isinstance(self.start.employee.tariff, type(None)):
            self.raise_user_error('enterper_notariff', (self.start.employee.party.rec_name))
        self.open_item(self.start.employee.tariff.type_present)
        return 'end'
    
# end PeriodAttendanceWizard
