# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
from unittest import TestCase

from click.testing import CliRunner

from revelation import cli


class CliTestCase(TestCase):
    def setUp(self):
        self.tests_folder = tempfile.mkdtemp()
        # save revealjs original folder
        self.revealjs_folder = cli.REVEALJS_FOLDER

    def tearDown(self):
        shutil.rmtree(self.tests_folder)
        # revert REVEALJS_FOLDER overrides
        self.original_revealjs_path()

    def fake_revealjs_instalation(self):
        cli.REVEALJS_FOLDER = os.path.join(self.tests_folder, "revealjs")
        os.mkdir(cli.REVEALJS_FOLDER)

    def original_revealjs_path(self):
        cli.REVEALJS_FOLDER = self.revealjs_folder

    def test_mkpresentation(self):
        presentation_folder = os.path.join(
            self.tests_folder, "test_mkpresentation"
        )
        presentation_file = os.path.join(presentation_folder, "slides.md")
        media_folder = os.path.join(presentation_folder, "media")
        config_file = os.path.join(presentation_folder, "config.py")

        runner = CliRunner()
        result = runner.invoke(cli.mkpresentation, [presentation_folder])

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isdir(presentation_folder))
        self.assertTrue(os.path.isfile(presentation_file))
        self.assertTrue(os.path.isdir(media_folder))
        self.assertTrue(os.path.isfile(config_file))

    def test_mkstatic(self):
        self.fake_revealjs_instalation()

        base_folder = tempfile.mkdtemp(dir=self.tests_folder)
        _, presentation_file = tempfile.mkstemp(
            ".md", "slides", base_folder, "# Test\n"
        )
        output_folder = os.path.join(base_folder, "output")
        index_file = os.path.join(output_folder, "index.html")
        static_folder = os.path.join(output_folder, "static")

        runner = CliRunner()
        result = runner.invoke(
            cli.mkstatic, [presentation_file, "-o", output_folder]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isdir(output_folder))
        self.assertTrue(os.path.isfile(index_file))
        self.assertTrue(os.path.isdir(static_folder))
