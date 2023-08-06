import logging

log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)


class Matcher:
    def __init__(self, rules):
        self.comp = rules

    def check(self, text: str):
        return self.comp.check(text)


class And:
    def __init__(self, *args):
        self.triggers = args

    def check(self, message) -> bool:
        log.info("Checking And " + str(len(self.triggers)))
        res = True
        for t in self.triggers:
            if type(t) is str:
                res &= t in message
            else:
                res &= t.check(message)
                if not res:
                    break
        return res


class Or:
    def __init__(self, *args):
        self.triggers = args

    def check(self, message) -> bool:
        log.info("Checking Or " + str(len(self.triggers)))
        res = False
        for t in self.triggers:
            if type(t) is str:
                res |= t in message
            else:
                res |= t.check(message)
            if res:
                break
        return res


class Not:
    def __init__(self, *args):
        if len([*args]) != 1:
            log.error("Misconfigured Not, it's going to get weird")
        self.triggers = args

    def check(self, message) -> bool:
        log.info("Checking Not " + str(len(self.triggers)))
        if type(self.triggers[0]) is str:
            res = self.triggers[0] not in message
        else:
            res = not self.triggers[0].check(message)
        return res


class StartsWith:
    def __init__(self, *args):
        if len([*args]) != 1:
            log.error("Misconfigured Startswith, it's going to get weird")
        self.triggers = args

    def check(self, message: str) -> bool:
        log.info("Checking StartsWith " + str(len(self.triggers)))
        if type(self.triggers[0]) is str:
            res = message.startswith(self.triggers[0])
        else:
            res = self.triggers[0].check(message)
        return res
