import unittest
from nbformat.v4 import new_notebook, new_markdown_cell

from ..test_utils.test_utils import create_temp_course

from nbgrader.nbgraderformat import ValidationError
from e2xgrader.models import PresetModel
from e2xgrader.preprocessors import ValidateExtraCells


class TestClearSolutions(unittest.TestCase):
    def setUp(self):
        tmp_dir, coursedir = create_temp_course()
        self.nb = new_notebook()
        self.nb.cells = PresetModel(coursedir).get_question_preset("Single Choice")
        tmp_dir.cleanup()

    def test_invalid_notebook_with_extra_cells(self):
        with self.assertRaises(ValidationError):
            ValidateExtraCells().preprocess(self.nb, {})

    def test_valid_notebook_with_extra_cells(self):
        self.nb.cells[0].metadata.extended_cell.choice = ["1"]
        try:
            ValidateExtraCells().preprocess(self.nb, {})
            assert True
        except ValidationError:
            assert False

    def test_valid_notebook_without_extra_cells(self):
        self.nb.cells = [new_markdown_cell()]
        try:
            ValidateExtraCells().preprocess(self.nb, {})
            assert True
        except ValidationError:
            assert False
