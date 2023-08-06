class Validator:
    def __init__(self, asserts):
        self.asserts = asserts

    def test(self, request):
        for a in self.asserts:
            a(request)
