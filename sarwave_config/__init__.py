import sarwaveifrproc.main
import hydra_zen
from pathlib import Path

def chunk_listing(path: str, i: int, n: int=10) -> str:
    l = Path(path).read_text().split()
    chunk_size = len(l)//(n - 1)
    Path('tmp').mkdir(exist_ok=True)
    Path(f'tmp/chunk_{i}_{Path(path).name}').write_text(
        '\n'.join(l[i*chunk_size:(i+1)*chunk_size])
    )
    return f'tmp/chunk_{i}_{Path(path).name}' 

hydra_zen.store(sarwaveifrproc.main.main, name='base')
hydra_zen.store(
    dict(header=sarwaveifrproc.main.main.__doc__),
    name='doc',
    group='hydra/help',
)

hydra_zen.store(
        dict(input_path=hydra_zen.builds(
            chunk_listing,
            path='???',
            i='${hydra:job.num}',
            n='${hydra:launcher.n_jobs}',
        )),
        name='chunk',
        group='parallel',
        package='_global_',
)

hydra_zen.store.add_to_hydra_store(overwrite_ok=True)
