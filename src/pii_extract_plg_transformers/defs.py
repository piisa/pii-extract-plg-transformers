
# Name of PIISA configuration section
FMT_CONFIG = "pii-extract-plg-transformers:main:v1"

# ----------------------------------------------------------------------

# Name of config field listing the PII instances to be detected
CFG_MAP = "pii_list"

# Block in configuration containing the task-specific settings
CFG_TASK = "task_config"
# Elements inside the task config
CFG_TASK_REUSE = "reuse_engine"
CFG_TASK_MODELS = "models"

# ----------------------------------------------------------------------

# Default values for task info
TASK_SOURCE = "piisa:pii-extract-plg-transformers"
TASK_DESCRIPTION = "Transformers-based PII tasks for some languages"
