import argparse
import os
import tempfile
import unittest
from typing import List, NamedTuple

import yattag

TOGGLE_JS = """
<script>
function toggle(elt) {
  var x = document.getElementById(elt);
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}
</script>
"""


class Result(NamedTuple):
    name: str
    status: str
    output: str

    def to_txt(self):
        return "{0}\t{1}".format(self.name, self.status.strip())

    def to_html(self, doc, tag, text):
        status = self.status.strip()
        if status == "ok":
            style = "color:green"
        else:
            style = "color:red"
        with tag("h3", style=style):
            text("{0} {1}".format(self.name, status))
        button = """<button onclick="toggle('{0}')">view output</button>""".format(
            self.name
        )
        doc.asis(button)
        with tag("div", id=self.name, style="display:none;"):
            with tag("pre"):
                text(self.output)


class Report(NamedTuple):
    results: List[Result]

    def to_txt(self):
        return "\n".join([res.to_txt() for res in self.results])

    def to_html(self):
        doc, tag, text = yattag.Doc().tagtext()
        doc.asis(TOGGLE_JS)
        for res in self.results:
            res.to_html(doc, tag, text)
        return doc.getvalue()


class CmpSpec(NamedTuple):
    name: str
    path: str

    def get_result(self) -> Result:
        status_path = os.path.join(self.path, "status")
        output_path = os.path.join(self.path, "h5diff.txt")

        if not os.path.exists(status_path) or not os.path.exists(output_path):
            return Result(name=self.name, status="bad_output", output="")
        else:
            with open(status_path, "r") as status_f, open(output_path, "r") as output_f:
                return Result(
                    name=self.name, status=status_f.read(), output=output_f.read()
                )


class ReportSpec(NamedTuple):
    specs: List[CmpSpec]

    def get_report(self):
        results = [cmp_spec.get_result() for cmp_spec in self.specs]
        results.sort(key=lambda res: (res.status, res.name))
        return Report(results)


def dir_to_ReportSpec(target_dir: str) -> ReportSpec:
    specs: List[CmpSpec] = []
    for output in sorted(os.listdir(target_dir)):
        path = os.path.join(target_dir, output)
        specs.append(CmpSpec(output, path))
    return ReportSpec(specs)


def make_dummy_output(target_path, status, output):
    os.mkdir(target_path)
    status_path = os.path.join(target_path, "status")
    output_path = os.path.join(target_path, "h5diff.txt")

    with open(status_path, "w") as f:
        f.write(status)

    with open(output_path, "w") as f:
        f.write(output)


class Test(unittest.TestCase):
    def test(self):
        with tempfile.TemporaryDirectory() as target_dir:
            a_path = os.path.join(target_dir, "a")
            b_path = os.path.join(target_dir, "b")

            make_dummy_output(a_path, "ok", "no output")

            report_spec = ReportSpec(
                [CmpSpec(name="a", path=a_path), CmpSpec(name="b", path=b_path)]
            )

            report = report_spec.get_report()

            self.assertEqual(report.results[1].status, "ok")
            self.assertEqual(report.results[0].status, "bad_output")

            print(report.to_txt())
            print(report.to_html())

    def test_example_comparison_output(self):
        report_spec = dir_to_ReportSpec("example_comparison_outputs")
        report = report_spec.get_report()
        print(report.to_txt())
        print(report.to_html())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--format", type=str, choices=["txt", "html"], required=True)
    args = parser.parse_args()

    report_spec = dir_to_ReportSpec(args.output_dir)
    report = report_spec.get_report()
    if args.format == "txt":
        print(report.to_txt())
    elif args.format == "html":
        print(report.to_html())
    else:
        raise Exception("unknown format {0}".format(args.format))
