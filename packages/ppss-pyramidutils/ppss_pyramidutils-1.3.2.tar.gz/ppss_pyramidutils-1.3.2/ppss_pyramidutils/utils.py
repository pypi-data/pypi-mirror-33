import logging,types

l = logging.getLogger(__name__)

class Utils():
    myconf = []

    @classmethod
    def confended(cls,**kwargs):
        pass

    @classmethod
    def config(cls,settings,prefix=None,defaultval = None):
        resvals = {}
        resdicts = {}
        if not prefix:
            prefix = cls.__name__.lower()
        for k in cls.myconf:
            if isinstance(k, types.StringTypes):
                prop = k
                key = prefix+"."+k
                default = defaultval
            else:
                try:
                    prop = k[0]
                    key = prefix+"."+k[0]
                    default = k[1]
                except:
                    continue

            value = settings.get(key,default)
            if "." in prop:
                propparts = prop.split(".")

                dictname = propparts[0]
                dictkey = propparts[1]
                if dictname not in resdicts:
                    resdicts[dictname] = {}
                resdicts[dictname][dictkey] = value
            else:
                setattr(cls,prop, value )
                if key in settings:
                    l.debug("value of {key} set to: {val}".format(key=prop,val=value ))
        for key,value in resdicts.items():
            setattr(cls,key, value )
            l.debug("value of {key} set to: {val}".format(key=key,val=value ))
                #setattr(cls,k,unicode(settings[key]) ) 
        cls.confended()