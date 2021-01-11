from app.main.exception_template import ExceptionTemplate


class RentIntegerException(ExceptionTemplate):
    pass


class MailToException(ExceptionTemplate):
    pass


class PayRequestException(ExceptionTemplate):
    pass


class MissingDataException(ExceptionTemplate):
    pass


class DbUpdateException(ExceptionTemplate):
    pass


class DataResolveException(ExceptionTemplate):
    pass


class OperationCancelledException(ExceptionTemplate):
    pass


class HtmlParseException(ExceptionTemplate):
    pass
