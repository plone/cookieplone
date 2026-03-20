from dataclasses import dataclass
from pathlib import Path

from cookieplone._types import RunConfig
from cookieplone.config import CookieploneState, generate_state
from cookieplone.generator.main import cookieplone
from cookieplone.repository import get_repository


@dataclass
class Result:
    """Holds the captured result of the cookieplone project generation."""

    _project_dir: Path | None = None
    exception: BaseException | None = None
    exit_code: int = 0
    context: dict | None = None

    @property
    def project_path(self) -> Path | None:
        """Return a path object if no exception occurred."""
        if self._project_dir is not None:
            return Path(self._project_dir)
        return None

    def __repr__(self) -> str:
        if self.exception:
            return f"<Result {self.exception!r}>"
        return f"<Result {self.project_path}>"


class Cookies:
    """Class to provide convenient access to the cookieplone API."""

    def __init__(self, template: str, output_factory, config_file):
        self._default_template = template
        self._output_factory = output_factory
        self._config_file = config_file
        self._counter = 0

    def _new_output_dir(self):
        dirname = f"bake{self._counter:02d}"
        output_dir = self._output_factory(dirname)
        self._counter += 1
        return Path(output_dir)

    def bake(
        self,
        extra_context: dict | None = None,
        template: str | None = None,
    ) -> Result:
        exception: BaseException | None = None
        exit_code = 0
        project_dir: Path | None = None

        if template is None:
            template = self._default_template

        # Load the context
        template_path = Path(template)

        repository_info = get_repository(
            template_path,
            template_path.name,
            "",
            "",
            True,
            True,
            "",
            str(self._config_file),
            False,
        )
        state: CookieploneState = generate_state(
            template_path=template_path, extra_context=extra_context
        )
        run_config = RunConfig(
            output_dir=self._new_output_dir(),
            no_input=True,
            accept_hooks=True,
            overwrite_if_exists=False,
            skip_if_file_exists=False,
            keep_project_on_failure=False,
        )
        try:
            # Run cookiecutter to generate a new project
            project_dir = cookieplone(
                repository_info=repository_info, state=state, run_config=run_config
            )
        except SystemExit as e:
            if e.code != 0:
                exception = e
            exit_code = int(e.code)
        except Exception as e:
            exception = e
            exit_code = -1

        return Result(
            exception=exception,
            exit_code=exit_code,
            _project_dir=project_dir,
            context=state.answers.answers,
        )
