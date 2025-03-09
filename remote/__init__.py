from js import document
from wwwpy.remote import micropip_install


async def main():
    from wwwpy.remote import shoelace
    shoelace.setup_shoelace()

    document.body.innerHTML = 'Installing pip libraries<br>'
    for lib in ['numpy', 'pandas', 'fastparquet']:
        document.body.insertAdjacentHTML('beforeend', f'<div>Installing {lib}...</div>')
        await micropip_install(lib)
    _fix_numpy()

    from . import component1  # for component registration
    document.body.innerHTML = '<component-1></component-1>'


def _fix_numpy():
    import numpy as np
    np.float_ = np.float64
