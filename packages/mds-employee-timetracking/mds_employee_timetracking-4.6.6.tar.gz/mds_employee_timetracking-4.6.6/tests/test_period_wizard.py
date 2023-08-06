# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.wizard import Wizard
from datetime import timedelta, datetime
from time import sleep
from trytond.modules.company.tests import set_company
from trytond.modules.employee_timetracking.tests.testlib import create_tariff_full, create_period, create_employee
from trytond.modules.employee_timetracking.period_wizard import CURRSTAT_PRESENT, \
    CURRSTAT_SITEWORK, CURRSTAT_ACTIVE, CURRSTAT_ABSENT


class PeriodWizardTestCase(ModuleTestCase):
    'Test period-wizard module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_period_attendance_wizard_start_on_change_employee(self):
        """ test: run on-change-employee with different period-items
        """
        pool = Pool()
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
                type_sitework = 'Site work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            employee1 = create_employee(tarobj1.company, name='Frida')
            self.assertTrue(employee1)
            employee1.tariff = tarobj1
            employee1.save()
    
            # run wizard view
            wiz_start = pool.get('employee_timetracking.wizperiod_attendance.start')
            obj1 = wiz_start()
            obj1.employee = employee1
            obj1.on_change_employee()
            
            self.assertEqual(obj1.company, employee1.company)
            
            # no period exist until now
            self.assertEqual(str(obj1.currstate), CURRSTAT_ABSENT)
            self.assertEqual(str(obj1.currtype), '')
            self.assertEqual(str(obj1.currperiod), '')
            self.assertEqual(obj1.currstart, None)
        
            # add work time item, begin, no end
            create_period(datetime(2018, 3, 10, 10, 30, 0), None, tarobj1.type_present, employee1)
            obj1.on_change_employee()
            self.assertEqual(obj1.currstate, CURRSTAT_PRESENT)
            self.assertEqual(obj1.currtype, tarobj1.type_present.name)
            self.assertEqual(str(obj1.currstart), '2018-03-10 10:30:00')
    
            # add site work item, 1 day later, begin, no end
            create_period(datetime(2018, 3, 11, 10, 30, 0), None, tarobj1.type_sitework, employee1)
            obj1.on_change_employee()
            self.assertEqual(obj1.currstate, CURRSTAT_SITEWORK)
            self.assertEqual(obj1.currtype, tarobj1.type_sitework.name)
            self.assertEqual(str(obj1.currstart), '2018-03-11 10:30:00')
    
            # add ill item, 1 day later, begin, no end
            Presence = pool.get('employee_timetracking.presence')
            l1 = Presence.search([('company', '=', employee1.company), ('name', '=', 'Ill')])
            create_period(datetime(2018, 3, 12, 8, 0, 0), None, l1[0], employee1)
            obj1.on_change_employee()
            self.assertEqual(obj1.currstate, CURRSTAT_ACTIVE)
            self.assertEqual(obj1.currtype, l1[0].name)
            self.assertEqual(str(obj1.currstart), '2018-03-12 08:00:00')
    
            # add work time item, begin+end
            create_period(datetime(2018, 3, 13, 8, 30, 0), datetime(2018, 3, 13, 16, 30, 0), tarobj1.type_present, employee1)
            obj1.on_change_employee()
            self.assertEqual(obj1.currstate, CURRSTAT_ABSENT)
            self.assertEqual(obj1.currtype, '')
            self.assertEqual(obj1.currstart, None)
            self.assertEqual(obj1.currperiod, '')
    
            # add 2 work time items, begin+no-end, no-begin+end
            create_period(datetime(2018, 3, 15, 8, 30, 0), None, tarobj1.type_present, employee1)
            create_period(None, datetime(2018, 3, 14, 16, 30, 0), tarobj1.type_present, employee1)
            obj1.on_change_employee()
            self.assertEqual(obj1.currstate, CURRSTAT_PRESENT)
            self.assertEqual(obj1.currtype, tarobj1.type_present.name)
            self.assertEqual(str(obj1.currstart), '2018-03-15 08:30:00')
    
            # add 2 work time items, no-begin+end, begin+no-end
            create_period(None, datetime(2018, 3, 17, 16, 30, 0), tarobj1.type_present, employee1)
            create_period(datetime(2018, 3, 16, 8, 30, 0), None, tarobj1.type_present, employee1)
            obj1.on_change_employee()
            self.assertEqual(obj1.currstate, CURRSTAT_ABSENT)
            self.assertEqual(obj1.currtype, '')
            self.assertEqual(obj1.currstart, None)
            self.assertEqual(obj1.currperiod, '')

    @with_transaction()
    def test_period_attendance_wizard_start_get_delta(self):
        """ test: get timedelta 
        """
        wiz_start = Pool().get('employee_timetracking.wizperiod_attendance.start')
        obj1 = wiz_start()
        self.assertEqual(str(obj1.get_delta(datetime.now() - timedelta(seconds=5*60))), '0:05:00')
        self.assertEqual(str(obj1.get_delta(datetime.now() - timedelta(seconds=5*60 + 15))), '0:05:00')
        self.assertEqual(str(obj1.get_delta(datetime.now() - timedelta(days=2, seconds=5*60))), '2 days, 0:05:00')

    @with_transaction()
    def test_period_attendance_wizard_start_format_timedelta(self):
        """ test: convert timedelta to string
        """
        wiz_start = Pool().get('employee_timetracking.wizperiod_attendance.start')
        
        obj1 = wiz_start()
        self.assertEqual(
                obj1.format_timedelta(timedelta(seconds=60*60*5 + 60*24, days=2)), 
                '2 d, 5 h, 24 m'
            )
        self.assertEqual(
                obj1.format_timedelta(timedelta(seconds=60*60*5 + 60*24, days=0)), 
                '5 h, 24 m'
            )
        self.assertEqual(
                obj1.format_timedelta(timedelta(seconds=60*60*18 + 60*25, days=0)), 
                '18 h, 25 m'
            )
        self.assertEqual(
                obj1.format_timedelta(timedelta(seconds=60*60*18 + 60*25 + 15, days=0)), 
                '18 h, 25 m'
            )

    @with_transaction()
    def test_period_attendance_wizard_start_worktime(self):
        """ test: create tariff+employee, start work time
        """
        pool = Pool()
        
        # prepare tariff + employee
        tarobj1 = create_tariff_full(tarname='Tariff1', tarshort='T1', 
                companyname='m-ds 1',
                breaktimes=[],
                timeaccounts=[],
                accountrules=[],
                presences=[
                        {'name':'Work', 'shortname':'1'},
                        {'name':'Ill', 'shortname':'2'},
                        {'name':'Site work', 'shortname':'3'}
                    ],
                type_work = 'Work',
                type_sitework = 'Site work',
            )
        self.assertTrue(tarobj1)
        with set_company(tarobj1.company):
            transaction = Transaction()
            employee1 = create_employee(tarobj1.company, name='Frieda')
            self.assertTrue(employee1)
            transaction.set_context(employee=employee1.id)
        
            PerAttndWizard = pool.get('employee_timetracking.wizperiod_attendance', type='wizard')
            Period = pool.get('employee_timetracking.period')
    
            # start wizard
            (sess_id, start_state, end_state) = PerAttndWizard.create()
            w_obj = PerAttndWizard(sess_id)
            
            # transitions fire exception w/o employee
            self.assertRaises(Exception, w_obj.transition_coming)
            self.assertRaises(Exception, w_obj.transition_going)
            self.assertRaises(Exception, w_obj.transition_startsite)
            self.assertRaises(Exception, w_obj.transition_endsite)
            
            w_obj.start.employee = employee1
            
            # transitions fire exception w/o tariff on employee
            self.assertRaises(Exception, w_obj.transition_coming)
            self.assertRaises(Exception, w_obj.transition_going)
            self.assertRaises(Exception, w_obj.transition_startsite)
            self.assertRaises(Exception, w_obj.transition_endsite)
            self.assertRaises(Exception, w_obj.start.on_change_employee)
    
            employee1.tariff = tarobj1
            employee1.save()
            w_obj.start.on_change_employee()
            
            # start work item
            w_obj.transition_coming()
            p_lst = Period.search([('employee', '=', employee1)])
            self.assertEqual(len(p_lst), 1)
            self.assertEqual(p_lst[0].presence, tarobj1.type_present)
            self.assertEqual(isinstance(p_lst[0].startpos, type(None)), False)
            self.assertEqual(isinstance(p_lst[0].endpos, type(None)), True)
            
            # wait - otherwise: startpos > endpos --> exception
            sleep(6.0)
            
            # start site work (the still open work time will be closed)
            w_obj.transition_startsite()
            s_lst = Period.search([('employee', '=', employee1), ('presence', '=', tarobj1.type_sitework)])
            self.assertEqual(len(s_lst), 1)
            self.assertEqual(s_lst[0].presence, tarobj1.type_sitework)
            self.assertEqual(isinstance(s_lst[0].startpos, type(None)), False)
            self.assertEqual(isinstance(s_lst[0].endpos, type(None)), True)
            # work item is closed by 'startsite'
            self.assertEqual(isinstance(p_lst[0].endpos, type(None)), False)
            
            # end site work
            sleep(1.5)
            w_obj.transition_endsite()
            self.assertEqual(isinstance(s_lst[0].endpos, type(None)), False)
            
            # stop wizard
            PerAttndWizard.delete(sess_id)
        
# end PeriodWizardTestCase
