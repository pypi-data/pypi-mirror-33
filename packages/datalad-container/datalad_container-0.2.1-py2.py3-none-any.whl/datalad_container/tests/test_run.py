import os.path as op

from datalad.api import Dataset
from datalad.api import create
from datalad.api import containers_add
from datalad.api import containers_run
from datalad.api import containers_list

from datalad.tests.utils import ok_clean_git
from datalad.tests.utils import assert_result_count
from datalad.tests.utils import with_tempfile
from datalad.utils import on_windows


testimg_url = 'shub://datalad/datalad-container:testhelper'


@with_tempfile
def test_container_files(path):
    ds = Dataset(path).create()
    # plug in a proper singularity image
    ds.containers_add(
        'mycontainer',
        url=testimg_url,
        image='righthere',
        # the next one is auto-guessed
        #call_fmt='singularity exec {img} {cmd}'
    )
    assert_result_count(
        ds.containers_list(), 1,
        path=op.join(ds.path, 'righthere'),
        name='mycontainer',
        updateurl=testimg_url)
    ok_clean_git(path)
    # now we can run stuff in the container
    # and because there is just one, we don't even have to name the container
    res = ds.containers_run(['dir'] if on_windows else ['ls'])
    # container becomes an 'input' for `run` -> get request, but "notneeded"
    assert_result_count(
        res, 1, action='get', status='notneeded',
        path=op.join(ds.path, 'righthere'), type='file')
    # this command changed nothing
    assert_result_count(
        res, 1, action='add', status='notneeded', path=ds.path, type='dataset')
