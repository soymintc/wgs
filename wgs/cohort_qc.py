import os

import pypeliner
import pypeliner.managed as mgd
from wgs.config import config
from wgs.utils import helpers


def cohort_qc_workflow(args):
    pypeline = pypeliner.app.Pypeline(config=args)

    workflow = pypeliner.workflow.Workflow(ctx=helpers.get_default_ctx(docker_image=config.containers('wgs')))

    inputs = helpers.load_yaml(args['input_yaml'])
    out_dir = args["out_dir"]
    tmp_dir = args["tmpdir"]
    api_key = args["API_key"]

    cohort_mafs = {cohort_label: data["cohort_maf"] for cohort_label, data in inputs.items()}

    report_path = os.path.join(out_dir, '{cohort_label}', "report.html")

    workflow.setobj(
        obj=mgd.OutputChunks('cohort_label'),
        value=list(inputs.keys()),
    )

    workflow.subworkflow(
        name="run_cohort_qc_workflow",
        func="wgs.workflows.cohort_qc.create_cohort_qc_workflow",
        axes=("cohort_label",),
        args=(
            mgd.InputInstance("cohort_label", ),
            api_key,
            out_dir,
            mgd.InputFile('cohort_maf', 'cohort_label', fnames=cohort_mafs),
            mgd.OutputFile('report_path', 'cohort_label', template=report_path),

        ),
    )

    pypeline.run(workflow)
