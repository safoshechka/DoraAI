import logging
import sys
import yaml
import argparse

from dora_ai import DoraAI


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", action="store", required=True)
    parser.add_argument("--logs", action="store", required=True)
    args = parser.parse_args()
    config_file = args.config if args.config else ""
    logs_file = args.logs if args.logs else ""

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler = logging.FileHandler(logs_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    sys_handler = logging.StreamHandler(sys.stdout)
    sys_handler.setLevel(logging.DEBUG)
    sys_handler.setFormatter(formatter)
    logger.addHandler(sys_handler)

    with open(config_file, "r") as c:
        config = yaml.load(c, Loader=yaml.Loader)

    dora = DoraAI(config)
    dora.run_bot()
