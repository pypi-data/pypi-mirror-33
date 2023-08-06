import os
import datetime
import platform

__all__ = ['runtimestamp']

def runtimestamp(user=None):
    '''
    Returns Runtime Metadata for Jupyter Notebooks
    '''
    if not user:
        user = os.environ.get("USER")
    today = datetime.datetime.now()
    version = platform.python_version()
    os_platform = platform.platform()
    
    print(
        "Updated {today}\nBy {user}\nUsing Python {version}\nOn {os_platform}".format(
            today = today,
            user = user,
            version = version,
            os_platform = os_platform
        )
    )
