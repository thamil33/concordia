import os

from concordia.language_model.base_openrouter_model import \
    BaseOpenRouterLanguageModel
from concordia.language_model.call_limit_wrapper import CallLimitLanguageModel
from concordia.language_model.language_model import DEFAULT_STATS_CHANNEL
from concordia.language_model.retry_wrapper import RetryLanguageModel
from concordia.utils import measurements as measurements_lib
import dotenv

dotenv.load_dotenv()

api_key = os.environ.get("OPENROUTER_API_KEY", "")
model_name = os.environ.get("OPENROUTER_MODEL", '') or 'mistralai/mistral-small-3.1-24b-instruct:free'


class OpenRouterLanguageModel(BaseOpenRouterLanguageModel):
    def __init__(
        self,
        model_name: str = model_name,
        api_key: str = api_key,
        measurements: measurements_lib.Measurements | None = None,
        channel: str = DEFAULT_STATS_CHANNEL,
        verbose_logging: bool = False,
    ):
        super().__init__(
            model_name=model_name,
            api_key=api_key,
            measurements=measurements,
            channel=channel,
            verbose_logging=verbose_logging,
        )

    @classmethod
    def with_wrappers(
        cls,
        model_name: str,
        api_key: str = None,
        measurements: measurements_lib.Measurements | None = None,
        channel: str = DEFAULT_STATS_CHANNEL,
        verbose_logging: bool = False,
        retry_on_exceptions=(Exception,),
        retry_tries: int = 3,
        retry_delay: float = 2.0,
        jitter: tuple[float, float] = (0.0, 1.0),
        max_calls: int = 1200,
    ):
        base = cls(
            model_name=model_name,
            api_key=api_key,
            measurements=measurements,
            channel=channel,
            verbose_logging=verbose_logging,
        )
        wrapped = RetryLanguageModel(
            base,
            retry_on_exceptions=retry_on_exceptions,
            retry_tries=retry_tries,
            retry_delay=retry_delay,
            jitter=jitter,
        )
        wrapped = CallLimitLanguageModel(wrapped, max_calls=max_calls)
        return wrapped
