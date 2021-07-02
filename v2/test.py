class ParticipantFrames:
    def __init__(self,**kwargs) -> None:
        for x in kwargs:
            self.__dict__[x] = kwargs[x]

kwargs  = {"ee":1,"qww":2,"sdf":3,'position':{'x':5,'y':6}}
a = ParticipantFrames(**kwargs)
print(a.position)