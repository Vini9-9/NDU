class GameAlreadyExistsException(Exception):
    def __init__(self, message="Não é possível substituir um jogo que já existe."):
        self.message = message
        super().__init__(self.message)

class FileNotFoundErrorException(Exception):
    def __init__(self, message="O arquivo de dados não foi encontrado."):
        self.message = message
        super().__init__(self.message)
