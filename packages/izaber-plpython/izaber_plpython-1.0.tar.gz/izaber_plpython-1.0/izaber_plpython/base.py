
class IPLPY(object):

    def __init__(self,plpy_globals,*args,**kwargs):
        self.configure(**plpy_globals)

    def configure(self,**kwargs):
        self.__dict__.update({
            'plpy': kwargs.get('plpy'),
            'TD': kwargs.get('TD'),
            'SD': kwargs.get('TD'),
            'GD': kwargs.get('GD')
        })

    def always_reload(self,active=True):
        self.GD['always_reload'] = active

    def q(self,query,types=[],args=[]):
        plan = self.plpy.prepare(query,types)
        return self.plpy.execute(plan,args)

    def __getattr__(self,k):
        return getattr(self.plpy,k)

