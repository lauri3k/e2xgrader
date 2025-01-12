import os
import sys

from tornado import web
from nbgrader.api import MissingEntry
from nbgrader.server_extensions.formgrader.base import (
    BaseHandler,
    check_xsrf,
    check_notebook_dir,
)
from nbgrader.server_extensions.formgrader.handlers import (
    SubmissionNavigationHandler as NbgraderSubmissionNavigationHandler,
)
from ...exporters import (
    GradeTaskExporter,
    GradeNotebookExporter,
    GradeAssignmentExporter,
)

from ...models import TemplateModel, ExerciseModel, TaskPoolModel


class ExportGradesHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    def get(self):
        html = self.render("export_grades.tpl", base_url=self.base_url)
        self.write(html)


class ExportAssignmentGradesHandler(BaseHandler):
    def initialize(self):
        self.__exporter = GradeAssignmentExporter(self.gradebook)

    @web.authenticated
    @check_xsrf
    def get(self):
        self.set_header("Content-Type", 'text/csv; charset="utf-8"')
        self.set_header("Content-Disposition", "attachment; filename=grades.csv")
        self.write(self.__exporter.make_table().to_csv(index=False))
        self.finish()


class ExportNotebookGradesHandler(BaseHandler):
    def initialize(self):
        self.__exporter = GradeNotebookExporter(self.gradebook)

    @web.authenticated
    @check_xsrf
    def get(self):
        self.set_header("Content-Type", 'text/csv; charset="utf-8"')
        self.set_header("Content-Disposition", "attachment; filename=grades.csv")
        self.write(self.__exporter.make_table().to_csv(index=False))
        self.finish()


class ExportTaskGradesHandler(BaseHandler):
    def initialize(self):
        self.__exporter = GradeTaskExporter(self.gradebook)

    @web.authenticated
    @check_xsrf
    def get(self):
        self.set_header("Content-Type", 'text/csv; charset="utf-8"')
        self.set_header("Content-Disposition", "attachment; filename=grades.csv")
        self.write(self.__exporter.make_table().to_csv(index=False))
        self.finish()


class GradebookAssignmentsHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    def get(self):
        view = self.get_argument("view", "notebook")
        if view == "task":
            template = os.path.join("task_view", "gradebook_assignments.tpl")
        else:
            template = "gradebook_assignments.tpl"
        html = self.render(template, base_url=self.base_url)
        self.write(html)


class GradebookNotebooksHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    def get(self, assignment_id):
        view = self.get_argument("view", "notebook")
        if view == "task":
            template = os.path.join("task_view", "gradebook_notebooks.tpl")
        else:
            template = "gradebook_notebooks.tpl"
        html = self.render(
            template, assignment_id=assignment_id, base_url=self.base_url
        )
        self.write(html)


class GradebookTasksHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    def get(self, assignment_id, notebook_id):
        html = self.render(
            "task_view/gradebook_tasks.tpl",
            assignment_id=assignment_id,
            notebook_id=notebook_id,
            base_url=self.base_url,
        )
        self.write(html)


class GradebookNotebookSubmissionsHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    def get(self, assignment_id, notebook_id):
        view = self.get_argument("view", "notebook")
        if view == "task":
            template = os.path.join("task_view", "gradebook_notebook_submissions.tpl")
        else:
            template = "gradebook_notebook_submissions.tpl"
        task_id = self.get_argument("filter", "")

        html = self.render(
            template,
            assignment_id=assignment_id,
            notebook_id=notebook_id,
            base_url=self.base_url,
            task_id=task_id,
        )
        self.write(html)


class SubmissionNavigationHandler(NbgraderSubmissionNavigationHandler):
    def _assignment_notebook_list_url(self, assignment_id, notebook_id, task_id):
        if len(task_id) < 1:
            return "{}/formgrader/gradebook/{}/{}".format(
                self.base_url, assignment_id, notebook_id
            )
        return "{}/formgrader/gradebook/{}/{}/?view=task&filter={}".format(
            self.base_url, assignment_id, notebook_id, task_id
        )

    def _next(self, assignment_id, notebook_id, submission, task_id):
        # find next submission
        submission_ids = self._get_submission_ids(assignment_id, notebook_id)
        ix = submission_ids.index(submission.id)
        if ix == (len(submission_ids) - 1):
            return self._assignment_notebook_list_url(
                assignment_id, notebook_id, task_id
            )
        else:
            return self._submission_url(submission_ids[ix + 1]) + "?task={}".format(
                task_id
            )

    def _prev(self, assignment_id, notebook_id, submission, task_id):
        # find previous submission
        submission_ids = self._get_submission_ids(assignment_id, notebook_id)
        ix = submission_ids.index(submission.id)
        if ix == 0:
            return self._assignment_notebook_list_url(
                assignment_id, notebook_id, task_id
            )
        else:
            return self._submission_url(submission_ids[ix - 1]) + "?task={}".format(
                task_id
            )

    def _next_incorrect(self, assignment_id, notebook_id, submission, task_id):
        # find next incorrect submission
        submission_ids = self._get_incorrect_submission_ids(
            assignment_id, notebook_id, submission
        )
        ix_incorrect = submission_ids.index(submission.id)
        if ix_incorrect == (len(submission_ids) - 1):
            return self._assignment_notebook_list_url(
                assignment_id, notebook_id, task_id
            )
        else:
            return self._submission_url(
                submission_ids[ix_incorrect + 1]
            ) + "?task={}".format(task_id)

    def _prev_incorrect(self, assignment_id, notebook_id, submission, task_id):
        # find previous incorrect submission
        submission_ids = self._get_incorrect_submission_ids(
            assignment_id, notebook_id, submission
        )
        ix_incorrect = submission_ids.index(submission.id)
        if ix_incorrect == 0:
            return self._assignment_notebook_list_url(
                assignment_id, notebook_id, task_id
            )
        else:
            return self._submission_url(
                submission_ids[ix_incorrect - 1]
            ) + "?task={}".format(task_id)

    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    def get(self, submission_id, action):
        try:
            submission = self.gradebook.find_submission_notebook_by_id(submission_id)
            assignment_id = submission.assignment.assignment.name
            notebook_id = submission.notebook.name
            task_id = self.get_argument("task", "")
        except MissingEntry:
            raise web.HTTPError(404, "Invalid submission: {}".format(submission_id))

        handler = getattr(self, "_{}".format(action))
        self.redirect(
            handler(assignment_id, notebook_id, submission, task_id), permanent=False
        )


class SubmissionHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    def get(self, submission_id):
        try:
            submission = self.gradebook.find_submission_notebook_by_id(submission_id)
            assignment_id = submission.assignment.assignment.name
            notebook_id = submission.notebook.name
            student_id = submission.student.id
        except MissingEntry:
            raise web.HTTPError(404, "Invalid submission: {}".format(submission_id))

        # redirect if there isn't a trailing slash in the uri
        if os.path.split(self.request.path)[1] == submission_id:
            url = self.request.path + "/"
            if self.request.query:
                url += "?" + self.request.query
            return self.redirect(url, permanent=True)

        filename = os.path.join(
            os.path.abspath(
                self.coursedir.format_path(
                    self.coursedir.autograded_directory, student_id, assignment_id
                )
            ),
            "{}.ipynb".format(notebook_id),
        )
        relative_path = os.path.relpath(filename, self.coursedir.root)
        indices = self.api.get_notebook_submission_indices(assignment_id, notebook_id)
        ix = indices.get(submission.id, -2)

        task_id = self.get_argument("task", "")

        resources = {
            "assignment_id": assignment_id,
            "notebook_id": notebook_id,
            "submission_id": submission.id,
            "index": ix,
            "total": len(indices),
            "base_url": self.base_url,
            "mathjax_url": self.mathjax_url,
            "student": student_id,
            "last_name": submission.student.last_name,
            "first_name": submission.student.first_name,
            "notebook_path": self.url_prefix + "/" + relative_path,
            "keyword": task_id,
        }

        if not os.path.exists(filename):
            resources["filename"] = filename
            html = self.render("formgrade_404.tpl", resources=resources)
            self.clear()
            self.set_status(404)
            self.write(html)

        else:
            html, _ = self.exporter.from_filename(filename, resources=resources)
            self.write(html)


class TaskcreatorHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    def get(self):
        self.redirect(f"{self.base_url}/taskcreator/assignments")


class ManageAssignmentsHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    def get(self):
        html = self.render(
            os.path.join("nbassignment", "assignments.tpl"),
            url_prefix=self.url_prefix,
            base_url=self.base_url,
            windows=(sys.prefix == "win32"),
        )
        self.write(html)


class ManageExercisesHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    def get(self, assignment):
        html = self.render(
            os.path.join("nbassignment", "exercises.tpl"),
            url_prefix=self.url_prefix,
            base_url=self.base_url,
            assignment=assignment,
            windows=(sys.prefix == "win32"),
        )
        self.write(html)


class ManagePoolsHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    def get(self):
        html = self.render(
            os.path.join("nbassignment", "taskpools.tpl"),
            url_prefix=self.url_prefix,
            base_url=self.base_url,
            windows=(sys.prefix == "win32"),
        )
        self.write(html)


class ManageTasksHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    def get(self, pool):
        html = self.render(
            os.path.join("nbassignment", "tasks.tpl"),
            url_prefix=self.url_prefix,
            base_url=self.base_url,
            pool=pool,
            windows=(sys.prefix == "win32"),
        )
        self.write(html)


class ManageTemplatesHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    def get(self):
        html = self.render(
            os.path.join("nbassignment", "templates.tpl"),
            url_prefix=self.url_prefix,
            base_url=self.base_url,
            windows=(sys.prefix == "win32"),
        )
        self.write(html)


class EditExercisesHandler(BaseHandler):
    def initialize(self):
        self._model = ExerciseModel(self.coursedir)

    @web.authenticated
    @check_xsrf
    @check_notebook_dir
    def get(self, assignment, exercise):
        html = self.render(
            os.path.join("nbassignment", "editexercise.tpl"),
            url_prefix=self.url_prefix,
            base_url=self.base_url,
            exercise=exercise,
            assignment=assignment,
            templates=TemplateModel(self.coursedir).list(),
            pools=TaskPoolModel(self.coursedir).list(),
            windows=(sys.prefix == "win32"),
        )
        self.write(html)


root_path = os.path.dirname(__file__)
template_path = os.path.join(root_path, "templates")
static_path = os.path.join(root_path, "static")

_navigation_regex = r"(?P<action>next_incorrect|prev_incorrect|next|prev)"

formgrade_handlers = [
    (r"/formgrader/export_grades/?", ExportGradesHandler),
    (r"/formgrader/export_grades/assignments/?", ExportAssignmentGradesHandler),
    (r"/formgrader/export_grades/notebooks/?", ExportNotebookGradesHandler),
    (r"/formgrader/export_grades/tasks/?", ExportTaskGradesHandler),
    (r"/formgrader/gradebook/?", GradebookAssignmentsHandler),
    (r"/formgrader/gradebook/([^/]+)/?", GradebookNotebooksHandler),
    (r"/formgrader/gradebook/tasks/([^/]+)/([^/]+)/?", GradebookTasksHandler),
    (r"/formgrader/gradebook/([^/]+)/([^/]+)/?", GradebookNotebookSubmissionsHandler),
    (
        r"/formgrader/submissions/(?P<submission_id>[^/]+)/%s/?" % _navigation_regex,
        SubmissionNavigationHandler,
    ),
    (r"/formgrader/submissions/([^/]+)/?", SubmissionHandler),
]

nbassignment_handlers = [
    (r"/taskcreator/?", TaskcreatorHandler),
    (r"/taskcreator/assignments/?", ManageAssignmentsHandler),
    (r"/taskcreator/assignments/(?P<assignment>[^/]+)/?", ManageExercisesHandler),
    (r"/taskcreator/pools/?", ManagePoolsHandler),
    (r"/taskcreator/pools/(?P<pool>[^/]+)/?", ManageTasksHandler),
    (r"/taskcreator/templates/?", ManageTemplatesHandler),
    (
        r"/taskcreator/assignments/(?P<assignment>[^/]+)/(?P<exercise>[^/]+)/?",
        EditExercisesHandler,
    ),
]

default_handlers = formgrade_handlers + nbassignment_handlers
