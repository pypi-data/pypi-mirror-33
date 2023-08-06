import julia

class JuliaPreparation(object):

    __instance = None

    class __OnlyOne:

        def __init__(self):
            self.__julia_object = julia.Julia()
            self.__julia_object.using('PowerModels')
            self.__julia_object.using("RemoteOffGridMicrogrids")

        def get_julia_object(self):
            return self.__julia_object

    def __init__(self):
        if self.__instance == None:
            self.__instance = JuliaPreparation.__OnlyOne()

    def get_julia_object(self):
        return self.__instance.get_julia_object()
