import json
import os
import subprocess
from copy import deepcopy
from shlex import quote


STACK_NAME = os.environ["STACK_NAME"]


def json_dumps(obj):
    return json.dumps(obj, separators=(",", ":"))


def remove_keys_if(d: dict, callable_predicate):
    return {k: v for k, v in d.items() if not callable_predicate(k)}


def create_api_only_config(config: dict):
    config = remove_keys_if(deepcopy(config), lambda key: key == "volumes")
    config["services"] = remove_keys_if(config["services"], lambda key: key != "api")
    return config


def get_stack_config():
    stack_config = json.loads(os.environ["STACK_CONFIG"])
    for key in stack_config:
        if not isinstance(stack_config[key], str):
            stack_config[key] = json_dumps(stack_config[key])
    return stack_config


def get_deploy_script(stack_config: dict):
    compose_config = create_api_only_config(stack_config)

    return f"""\
echo >stack.yml {quote(json_dumps(stack_config))}
echo >docker-compose.yml {quote(json_dumps(compose_config))}

echo "Deploying services"
docker stack deploy {quote(STACK_NAME)} --with-registry-auth --prune --compose-file stack.yml

echo "Upgrading API..."
sleep 5s
docker compose pull api
docker compose run --remove-orphans --quiet-pull --rm api sh exec/upgrade.sh
"""


def get_compose_config():
    config_ps = subprocess.run(
        ["docker", "stack", "config", "--compose-file", "docker-compose.yml"],
        stdout=subprocess.PIPE,
        check=True,
        env={**os.environ, **get_stack_config()},
    )

    # Remove networks.[].name keys and convert to json
    json_config_str = subprocess.run(
        ["yq", "-o=json", "del(.networks.[].name)"],
        input=config_ps.stdout,
        capture_output=True,
        check=True,
    ).stdout.decode()

    config = json.loads(json_config_str)
    return remove_keys_if(config, lambda key: key.startswith("x-"))


def main():
    os.makedirs(".pipeline_output", exist_ok=True)
    compose_config = get_compose_config()
    with open(".pipeline_output/deploy.sh", "w") as f:
        f.write(get_deploy_script(compose_config))


main()
