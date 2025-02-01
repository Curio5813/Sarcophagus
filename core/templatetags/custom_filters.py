from django import template

register = template.Library()

@register.filter
def calcular_estrelas(rating, i):
    """
    Calcula se a estrela deve estar ativa com base no rating do usuário.
    :param rating: Avaliação do usuário (de 0 a 10)
    :param i: Posição da estrela (1 a 5)
    :return: True se a estrela deve ser acesa, False caso contrário
    """
    if rating is None:  # Verifica se o rating é None
        return False
    try:
        estrelas_acesas = rating / 2  # Convertendo para escala de 5 estrelas
        i = int(i)  # Converte 'i' para inteiro
        return estrelas_acesas >= i
    except (ValueError, TypeError):
        return False


@register.filter
def mul(value, arg):
    """Multiplica o valor pelo argumento"""
    return int(value) * int(arg)