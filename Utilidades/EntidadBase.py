class EntidadBase:
    """Base de las clases de Entidades.

    Cada entidad declara en `Campos` los nombres de sus atributos (los mismos de las
    columnas y de lo que devuelven los procedimientos almacenados). Con eso la consola
    puede convertir una entidad en diccionario y viceversa usando sus Get/Set.
    """
    Campos: list = []

    @staticmethod
    def NombrePascal(campo: str) -> str:
        return "".join(parte.capitalize() for parte in campo.split("_"))

    def ADiccionario(self) -> dict:
        return {campo: getattr(self, "Get" + self.NombrePascal(campo))() for campo in self.Campos}

    def DesdeDiccionario(self, valores: dict) -> None:
        for campo in self.Campos:
            if campo in valores:
                getattr(self, "Set" + self.NombrePascal(campo))(valores[campo])
