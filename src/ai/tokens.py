class TokenCounter:
    def __init__(self):
        self._count = 0

    async def get(self):
        return self._count

    async def set(self, value):
        self._count = value

    async def add(self, value):
        self._count += value

    async def reset(self):
        self._count = 0
        
        
total_tokens = TokenCounter()