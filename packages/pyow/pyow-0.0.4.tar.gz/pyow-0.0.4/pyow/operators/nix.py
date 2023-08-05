from pyow.types import Predicate


def nix(predicate: Predicate) -> Predicate:
    def add_validator(validator) -> Predicate:
        fn = validator['validator']
        msg = validator['message']

        validator['message'] = lambda value, result=None: f'[NOT] {msg(value)}'
        validator['validator'] = lambda value: not fn(value)

        predicate.context['validators'].append(validator)
        return predicate

    predicate.add_validator = add_validator
    return predicate


def isnot(predicate: Predicate) -> Predicate:
    return nix(predicate)
