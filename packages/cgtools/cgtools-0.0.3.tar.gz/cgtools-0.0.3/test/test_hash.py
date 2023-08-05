


class TTT(object):

    def __init__(self):
        super(TTT, self).__init__()

    def __hash__(self):
        return '1'





t = []

n = TTT()
n2 = TTT()

t.append(n)

print(n2 in t)


