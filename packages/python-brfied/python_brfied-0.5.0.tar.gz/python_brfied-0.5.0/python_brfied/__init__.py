"""
The MIT License (MIT)

Copyright 2015 Umbrella Tech.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import re


__author__ = 'Kelson da Costa Medeiros <kelsoncm@gmail.com>'

UF_LIST = [("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"), ("BA", "Bahia"), ("CE", "Ceará"),
           ("DF", "Distrito Federal"), ("ES", "Espírito Santo"), ("GO", "Goiás"), ("MA", "Maranhão"),
           ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"), ("MG", "Minas Gerais"), ("PA", "Pará"),
           ("PB", "Paraíba"), ("PR", "Paraná"), ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"),
           ("RN", "Rio Grande do Norte"), ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"),
           ("SC", "Santa Catarina"), ("SP", "São Paulo"), ("SE", "Sergipe"), ("TO", "Tocantins")]
UF_SIGLAS = [x[0] for x in UF_LIST]
UF_NOMES = [x[1] for x in UF_LIST]

CPF_MASK = '999.999.999-00'
CPF_RE = re.compile(r'^(\d{3})\.(\d{3})\.(\d{3})-(\d{2})$')

CNPJ_MASK = '99.999.999/9999-00'
CNPJ_RE = re.compile('^(\d{2})[.-]?(\d{3})[.-]?(\d{3})/(\d{4})-(\d{2})$')

CEP_MASK = '99999-999'
CEP_RE = '^\d{5}-\d{3}$'

PROCESSO_MASK = '9999999-99.9999.9.99.9999'
PROCESSO_RE = re.compile('^(\d{7})-?(\d{2})\.?(\d{4})\.?(\d)\.?(\d{2})\.?(\d{4})$')


class ValidationException(Exception):
    pass


class EmptyMaskException(ValidationException):
    def __init__(self, message='Nenhuma máscara informada'):
        super(MaskException, self).__init__(message)


class MaskException(ValidationException):
    def __init__(self, message='Valor informado não está no formato correto'):
        super(MaskException, self).__init__(message)


class DVException(ValidationException):
    def __init__(self, message='Valor incorreto. Dígito verifcador inconsistente.'):
        super(DVException, self).__init__(message)


class MaskWithoutDigitsException(ValidationException):
    def __init__(self, message='A máscara não tem dígitos'):
        super(DVException, self).__init__(message)


class MaskWithoutDVException(ValidationException):
    def __init__(self, message='A máscara não tem dígitos verificador'):
        super(DVException, self).__init__(message)


class MaskWithoutSpecialCharsException(ValidationException):
    def __init__(self, message='A máscara só contém dígitos'):
        super(DVException, self).__init__(message)


def only_digits(seq):
    return ''.join(c for c in filter(type(seq).isdigit, seq))


def apply_mask(value, mask):
    unmask = only_digits(mask)
    zfill_value = only_digits(value).zfill(len(unmask))
    if len(unmask) != len(zfill_value):
        raise MaskException()

    result = ''
    i = 0
    for m in mask:
        if m.isdigit():
            result += zfill_value[i]
            i += 1
        else:
            result += m
    return result


def validate_masked_value(value, mask, force=True):
    masked_value = apply_mask(only_digits(value), mask) if force else value
    if len(mask) != len(masked_value):
        raise MaskException()

    for i in range(0, len(mask)):
        m = mask[i]
        v = masked_value[i]
        if (not m.isdigit() and m != v) or m.isdigit() != v.isdigit():
            raise MaskException()
    return masked_value


def validate_mod11(unmasked_value, num_digits, num_dvs):
    for v in range(num_dvs, 0, -1):
        num_digito = num_digits - v + 1
        dv = sum([i * int(unmasked_value[idx]) for idx, i in enumerate(range(num_digito, 1, -1))]) % 11
        calculated_dv = '%d' % (11 - dv if dv >= 2 else 0,)
        if calculated_dv != unmasked_value[-v]:
            raise DVException()


def validate_cpf(unmasked_value, *args, **kwargs):
    value = only_digits(unmasked_value)

    if len(value) != 11:
        raise MaskException('O CPF deve ter exatamente 11 digitos')

    dv1 = sum([int(value[i]) * (10-i) for i in range(0, 9)]) * 10 % 11
    dv2 = sum([int(value[i]) * (11-i) for i in range(0, 10)]) * 10 % 11
    dv1 = dv1 if dv1 != 10 else 0
    dv2 = dv2 if dv2 != 10 else 0

    if value[-2:] != "%d%d" % (dv1, dv2):
        raise DVException('O dígito verificador informado está inválido')


def validate_cnpj(unmasked_value, *args, **kwargs):
    value = only_digits(unmasked_value)

    if len(value) != 14:
        raise MaskException('O CNPJ ter exatamente 14 digitos')

    c1 = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    c2 = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    dv1 = sum([int(value[i]) * c1[i] for i in range(0, 12)])
    dv2 = sum([int(value[i]) * c2[i] for i in range(0, 13)])
    dv1 = 11 - dv1 % 11 if dv1 % 11 > 2 else 0
    dv2 = 11 - dv2 % 11 if dv2 % 11 > 2 else 0
    dvs = "%d%d" % (dv1, dv2)

    if value[-2:] != dvs:
        raise DVException('O dígito verificador informado está inválido')


def validate_mask(mask):
    if mask is None or mask == '':
        raise EmptyMaskException();

    unmask = only_digits(mask)

    if unmask.find('9') < 0:
        raise MaskWithoutDigitsException()

    # if unmask.find('0') < 0:
    #     raise MaskWithoutDVException()

    if len(unmask) == len(mask):
        raise MaskWithoutSpecialCharsException()


def validate_dv_by_mask(value, mask, force=True, validate_dv=validate_mod11):
    validate_mask(mask)
    unmask = only_digits(mask)
    masked_value = validate_masked_value(value, mask, force)
    unmasked_value = only_digits(masked_value)
    num_dvs = len([x for x in unmask if x == '0'])
    num_digits = len(unmask)
    validate_dv(unmasked_value, num_digits, num_dvs)
    return masked_value


def to_choice(*args):
    return [(x, x) for x in args]


class EstadoCivilChoices(object):
    SOLTEIRO = 'Solteiro(a)'
    CASADO = 'Casado(a)'
    DIVORCIADO = 'Divorciado(a)'
    SEPARADO = 'Separado(a)'
    VIUVO = 'Viúvo(a)'
    UNIAO_ESTAVEL = 'União estável'
    CHOICES = to_choice(SOLTEIRO, CASADO, DIVORCIADO, SEPARADO, VIUVO, UNIAO_ESTAVEL)

    def __init__(self):
        pass


class RacaChoices(object):
    NAO_DECLARADO = 'Não declarado'
    AMARELO = 'Amarelo(a)'
    INDIGENA = 'Indígena'
    PRETO = 'Preto(a)'
    BRANCO = 'Branco(a)'
    PARDO = 'Pardo(a)'
    CHOICES = to_choice(NAO_DECLARADO, AMARELO, INDIGENA, PRETO, BRANCO, PARDO)

    def __init__(self):
        pass


class SexoChoices(object):
    SEXO_MASCULINO = 'M'
    SEXO_FEMININO = 'F'
    SEXO_NAO_DECLARADO = 'F'
    CHOICES = [(SEXO_MASCULINO, 'Masculino'), (SEXO_FEMININO, 'Feminino'), (SEXO_NAO_DECLARADO, 'Não declarado')]

    def __init__(self):
        pass


class ZonaChoices(object):
    URBANA = 'Urbana'
    RURAL = 'Rural'
    CHOICES = to_choice(URBANA, RURAL)

    def __init__(self):
        pass


class RegiaoChoices(object):
    NORTE = 'N'
    NORDESTE = 'NE'
    SUDESTE = 'SE'
    SUL = 'S'
    CENTRO_OESTE = 'CO'
    CHOICES = ((NORTE, 'Norte'), (NORDESTE, 'Nordeste'), (SUDESTE, 'Sudeste'), (SUL, 'Sul'),
               (CENTRO_OESTE, 'Centro-Oeste'))

    def __init__(self):
        pass


class SimNaoNaoDeclaradoChoices(object):
    NAO_DECLARADO = 'I'
    NAO = 'N'
    SIM = 'S'
    CHOICES = [(NAO_DECLARADO, 'Não declarado'), (NAO, 'Não'), (SIM, 'Sim')]

    def __init__(self):
        pass


class NecessidadeEspecialChoices(object):
    CEGUEIRA = 'Cegueira'
    BAIXA_VISAO = 'Baixa visão'
    SURDEZ = 'Surdez'
    CHOICES = to_choice(CEGUEIRA, BAIXA_VISAO, SURDEZ)

    def __init__(self):
        pass
