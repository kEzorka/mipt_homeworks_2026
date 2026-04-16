import json
from datetime import UTC, datetime
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func_name: CallableWithMeta[P, R_co], block_time: datetime, message: str):
        super().__init__(message)
        self.func_name = f"{func_name.__module__}.{func_name.__name__}"
        self.block_time = block_time


def _is_positive_integer(number: Any) -> bool:
    return isinstance(number, int) and number > 0


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        errors: list[ValueError] = []

        if not _is_positive_integer(critical_count):
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if not _is_positive_integer(time_to_recover):
            errors.append(ValueError(INVALID_RECOVERY_TIME))

        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self._critical_count = critical_count
        self._time_to_recover = time_to_recover
        self._triggers_on = triggers_on

        self._count_of_blocks: int = 0
        self._block_time: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            self._reset_block_time(func)
            return self._call_func(func, *args, **kwargs)

        return wrapper

    def _reset_block_time(self, func: CallableWithMeta[P, R_co]) -> None:
        if self._block_time:
            passed_time: float = (datetime.now(UTC) - self._block_time).total_seconds()

            if passed_time < self._time_to_recover:
                raise BreakerError(func_name=func, block_time=self._block_time, message=TOO_MUCH)

            self._block_time = None

    def _call_func(self, func: CallableWithMeta[P, R_co], *args: P.args, **kwargs: P.kwargs) -> R_co:
        try:
            result = func(*args, **kwargs)
        except self._triggers_on as exception:
            self._count_of_blocks += 1
            if self._count_of_blocks < self._critical_count:
                raise

            self._count_of_blocks = 0
            self._block_time = datetime.now(UTC)

            raise BreakerError(func_name=func, block_time=self._block_time, message=TOO_MUCH) from exception
        else:
            self._count_of_blocks = 0
            return result


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
