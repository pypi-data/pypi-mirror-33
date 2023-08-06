# http://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Distributing%20Jupyter%20Extensions%20as%20Python%20Packages.html
from pathlib import Path


def _jupyter_server_extension_paths():
    return [{
        "module": "notebook_separate_output"
    }]


def redirect_output_pre_save(model, **kwargs):
    """redirect output before saving notebooks"""
    log = kwargs['contents_manager'].log
    ipynb = Path(kwargs['path'])
    outputfile = ipynb.with_suffix('.log')

    if model['type'] != 'notebook':
        return

    # only run on nbformat v4
    if model['content']['nbformat'] != 4:
        log.warning("nbformat v%s, not scrubbing output" % model['content']['nbformat'])
        return

    output = []
    for cell in model['content']['cells']:
        if cell['cell_type'] != 'code':
            continue
        output.append('> '+'\n> '.join(cell['source'].split('\n')))  # cell source
        output.extend([o['text'] for o in cell['outputs']])
        output.append('')
        cell['outputs'] = []
        cell['execution_count'] = None

    outputfile.write_text('\n'.join(output))


def load_jupyter_server_extension(nbapp):
    nbapp.contents_manager.pre_save_hook = redirect_output_pre_save
