from ciri.fields import FieldError
from ciri.exception import ValidationError, FieldValidationError

def range(min=None, max=None):
    def validate_range(value, schema=None, field=None, min=min, max=max):
        try:
            if min is not None and max is not None:
                if value < min or value > max:
                    raise Exception
            elif min is not None:
                if value < min:
                    raise Exception
            elif max is not None:
                if value > max:
                    raise Exception
        except Exception:
            raise FieldValidationError(FieldError(field, message='value is out of range'))
        return value
    return validate_range
