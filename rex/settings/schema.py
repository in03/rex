# import re
# from commonregex import link
# import os
# from schema import Schema, And, Optional


# settings_schema = Schema(
#     {
#         "app": {
#             "loglevel": lambda s: s
#             in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
#             "log_to_file": bool,
#             "logfile_path": lambda p: os.path.exists(p),
#         },
#         "backup": {
#             "in_project_dir": bool,
#             "in_static_dir": lambda p: os.path.exists(p),
#         },
#     },
#     ignore_extra_keys=True,
# )
