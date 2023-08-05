# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


# presence-type
# Defines which presence types exist for the employee.
# Presence types are used to determine what kind of recorded presence is, 
# e.g. 8h work, 3h duty outside the house, 2 days sick, etc.


from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Id
from trytond.transaction import Transaction


__all__ = ['PresenceType']
__metaclass__ = PoolMeta


class PresenceType(ModelSQL, ModelView):
    'Type of presence'
    __name__ = 'employee_timetracking.presence'
    
    name = fields.Char(string=u'Name', required=True)
    shortname = fields.Char(string=u'shorthand symbol', required=True, size=4,
        help=u'The shorthand symbol appears in the tables of the reports.')
    company = fields.Many2One(string=u'Company', model_name='company.company',
        states={
            'readonly': ~Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
        }, required=True, select=True)

    # views
    tariffmodel = fields.Function(fields.One2Many(string=u'used in Tariff model', readonly=True, field=None,
                    help=u'This presence type is used in the specified tariff models.',
                    model_name='employee_timetracking.tariffmodel'), 'on_change_with_tariffmodel')
    employees = fields.Function(fields.One2Many(model_name='company.employee', field=None,
        readonly=True, string=u'Used by Employees'), 'on_change_with_employees')

    @classmethod
    def __setup__(cls):
        super(PresenceType, cls).__setup__()
        tab_pres = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_name', 
            Unique(tab_pres, tab_pres.name, tab_pres.company), 
            u'This name is already in use.'),
            ('uniq_short', 
            Unique(tab_pres, tab_pres.shortname, tab_pres.company), 
            u'This shorthand symbol is already in use.'),
            ])
    
    @classmethod
    def default_company(cls):
        """ set active company to default
        """
        context = Transaction().context
        return context.get('company')
        
    @fields.depends('id')
    def on_change_with_employees(self, name=None):
        """ get employees which use this presence-type
        """
        pool = Pool()
        Period = pool.get('employee_timetracking.period')
        Employee = pool.get('company.employee')
        Presence = pool.get('employee_timetracking.presence')
        tab_per = Period.__table__()
        tab_empl = Employee.__table__()
        tab_pres = Presence.__table__()
        cursor = Transaction().connection.cursor()
        
        qu1 = tab_empl.join(tab_per, condition=tab_per.employee==tab_empl.id
                ).join(tab_pres, condition=tab_pres.id==tab_per.presence
                ).select(tab_empl.id,
                    where=tab_pres.id == self.id
                )
        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        return [x[0] for x in l1]

    @fields.depends('journal')
    def on_change_with_tariffmodel(self, name=None):
        """ get tariff models
        """
        Tariff = Pool().get('employee_timetracking.tariffmodel')
        l1 = Tariff.search([('presence', '=', self.id)])
        return [x.id for x in l1]

    @classmethod
    def create(cls, vlist):
        """ create item
        """
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('company'):
                values['company'] = cls.default_company()
        return super(PresenceType, cls).create(vlist)

# ende PresenceType

