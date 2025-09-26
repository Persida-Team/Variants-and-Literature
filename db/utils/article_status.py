from .enum_and_constants import ProcessingStageEnum, ArticleProcessingStatusEnum
from .model import ArticleProcessingStage, ProcessingStageHistory
import .model as model
from datetime import datetime, timezone
from functools import wraps


STAGE_ORDER = list(ProcessingStageEnum)


def next_stage(current: ProcessingStageEnum):
    try:
        return STAGE_ORDER[STAGE_ORDER.index(current) + 1]
    except IndexError:
        return ProcessingStageEnum.complete


class InvalidProcessingStageError(Exception):
    def __init__(self, current, expected):
        super().__init__(
            f"Invalid stage: expected '{expected.name}', but current is '{current.name}'"
        )


class FailedProcessingStageError(Exception):
    def __init__(self, article, stage, error):
        super().__init__(
            f"Failed processing stage '{stage.name}' for article {article.id}: {error}"
        )
        self.article = article
        self.stage = stage
        self.error = error


def requires_stage_and_advance(expected_stage: ProcessingStageEnum):
    def decorator(func):
        @wraps(func)
        def wrapper(article, session, *args, **kwargs):
            current = (
                article.processing_stage.current_stage
                if article.processing_stage
                else None
            )
            if current != expected_stage:
                raise InvalidProcessingStageError(current, expected_stage)
            try:
                result = func(article, session, *args, **kwargs)
                advance_stage(article, session, next_stage(expected_stage))
            except Exception as e:
                advance_stage(
                    article,
                    session,
                    next_stage(expected_stage),
                    status="error",
                    error=str(e),
                )
                raise FailedProcessingStageError(article, expected_stage, str(e))
            return result

        return wrapper

    return decorator


def advance_stage(
    article: model.Article,
    session,
    new_stage: ProcessingStageEnum,
    status=ArticleProcessingStatusEnum.success,
    error=None,
):
    if not isinstance(new_stage, ProcessingStageEnum):
        raise ValueError("new_stage must be an instance of ProcessingStageEnum")
    if not isinstance(status, ArticleProcessingStatusEnum):
        raise ValueError("status must be an instance of ArticleProcessingStatusEnum")

    now = datetime.now(timezone.utc)
    if not article.processing_stage:
        article.processing_stage = ArticleProcessingStage(
            article_id=article.id,
            current_stage=new_stage,
            updated_at=now,
            last_error=error,
        )
    else:
        article.processing_stage.current_stage = new_stage
        article.processing_stage.updated_at = now
        article.processing_stage.last_error = error

    session.add(
        ProcessingStageHistory(
            article_id=article.id,
            stage=new_stage,
            status=status,
            error_message=error,
            updated_at=now,
        )
    )

    session.commit()


@requires_stage_and_advance(ProcessingStageEnum.pending_download)
def mark_downloaded(article, session):
    article.download_status = model.DownloadStatus(is_downloaded=True, downloaded_date=datetime.now(timezone.utc))

@requires_stage_and_advance(ProcessingStageEnum.pending_parse_text)
def mark_text_parsed(article, session):
    article.text_status = model.TextParseStatus(is_parsed=True, parsed_date=datetime.now(timezone.utc))

