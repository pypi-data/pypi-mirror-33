class Handler:
    def __init__(self, inner, transformer=lambda x: x, postProcessor=None):
        self.inner = inner
        self.transformer = transformer
        self.postProcessor = postProcessor

    def __call__(self, payload, command):
        payload = self.transformer(payload)

        self.inner(payload, command)
        if self.postProcessor is not None:
            self.postProcessor(payload, command)
