import os
import json

from tornado import web
from nbgrader.server_extensions.formgrader.base import check_xsrf

from ...models import (
    PresetModel,
    AssignmentModel,
    ExerciseModel,
    TaskPoolModel,
    TaskModel,
    TemplateModel,
)
from .base import E2xBaseApiHandler as BaseApiHandler
from .base import BaseApiManageHandler, BaseApiListHandler

from ...utils import NotebookVariableExtractor
from ...converters import GenerateExercise
from jupyter_client.kernelspec import KernelSpecManager


class SolutionCellCollectionHandler(BaseApiHandler):
    @web.authenticated
    @check_xsrf
    def get(self, assignment_id, notebook_id):
        cells = self.api.get_solution_cell_ids(assignment_id, notebook_id)
        self.write(json.dumps(cells))


class SubmittedTaskCollectionHandler(BaseApiHandler):
    @web.authenticated
    @check_xsrf
    def get(self, assignment_id, notebook_id, task_id):
        submissions = self.api.get_task_submissions(assignment_id, notebook_id, task_id)
        self.write(json.dumps(submissions))


class PresetHandler(BaseApiHandler):
    def initialize(self):
        self.__model = PresetModel(self.coursedir)

    def _list_template(self):
        self.write(json.dumps(self.__model.list_template_presets()))

    def _get_template(self):
        name = self.get_argument("name")
        self.write(json.dumps(self.__model.get_template_preset(name)))

    def _list_question(self):
        self.write(json.dumps(self.__model.list_question_presets()))

    def _get_question(self):
        name = self.get_argument("name")
        self.write(json.dumps(self.__model.get_question_preset(name)))

    @web.authenticated
    @check_xsrf
    def get(self):
        action = self.get_argument("action")
        preset_type = self.get_argument("type")
        handler = getattr(self, "_{}_{}".format(action, preset_type))
        handler()


class TemplateVariableHandler(BaseApiHandler):
    @web.authenticated
    @check_xsrf
    def get(self):
        template = self.get_argument("template")
        variables = NotebookVariableExtractor().extract(
            os.path.join(
                self.url_prefix, "templates", template, "{}.ipynb".format(template)
            )
        )
        self.write(json.dumps(variables))


class KernelSpecHandler(BaseApiHandler):
    @web.authenticated
    @check_xsrf
    def get(self):
        self.write(json.dumps(KernelSpecManager().get_all_specs()))


class GenerateExerciseHandler(BaseApiHandler):
    @web.authenticated
    @check_xsrf
    def get(self):
        resources = json.loads(self.get_argument("resources"))
        GenerateExercise(coursedir=self.coursedir).convert(resources)
        self.write({"status": True})


formgrade_handlers = [
    (r"/formgrader/api/solution_cells/([^/]+)/([^/]+)", SolutionCellCollectionHandler),
    (
        r"/formgrader/api/submitted_tasks/([^/]+)/([^/]+)/([^/]+)",
        SubmittedTaskCollectionHandler,
    ),
]

nbassignment_handlers = [
    (r"/taskcreator/api/presets", PresetHandler),
    (
        r"/taskcreator/api/assignments/?",
        BaseApiListHandler,
        dict(model_cls=AssignmentModel),
    ),
    (
        r"/taskcreator/api/template/(?P<name>[^/]+)/?",
        BaseApiManageHandler,
        dict(model_cls=TemplateModel),
    ),
    (
        r"/taskcreator/api/templates/?",
        BaseApiListHandler,
        dict(model_cls=TemplateModel),
    ),
    (
        r"/taskcreator/api/pool/(?P<name>[^/]+)/?",
        BaseApiManageHandler,
        dict(model_cls=TaskPoolModel),
    ),
    (r"/taskcreator/api/pools/?", BaseApiListHandler, dict(model_cls=TaskPoolModel)),
    (
        r"/taskcreator/api/pools/(?P<pool>[^/]+)/?",
        BaseApiListHandler,
        dict(model_cls=TaskModel),
    ),
    (
        r"/taskcreator/api/task/(?P<pool>[^/]+)/(?P<name>[^/]+)/?",
        BaseApiManageHandler,
        dict(model_cls=TaskModel),
    ),
    (
        r"/taskcreator/api/exercise/(?P<assignment>[^/]+)/(?P<name>[^/]+)/?",
        BaseApiManageHandler,
        dict(model_cls=ExerciseModel),
    ),
    (
        r"/taskcreator/api/assignments/(?P<assignment>[^/]+)/?",
        BaseApiListHandler,
        dict(model_cls=ExerciseModel),
    ),
    (r"/taskcreator/api/templates/variables", TemplateVariableHandler),
    (r"/taskcreator/api/kernelspec", KernelSpecHandler),
    (r"/taskcreator/api/generate_exercise", GenerateExerciseHandler),
]

default_handlers = formgrade_handlers + nbassignment_handlers
