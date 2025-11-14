#!/usr/bin/env python3
import subprocess
from pathlib import Path


SOLR_CONTAINER = "song_solr"
CORES = ["simple", "songs"]

SYNONYMS_FILE = Path.cwd() / "solr" / "synonyms_hand.txt"
STOPWORDS_FILE = Path.cwd() / "solr" / "stopwords.txt"


def run_command(cmd, check=True):
    """Executa um comando shell e imprime saída."""
    print(f"> {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result



def create_core(core_name):
    cmd = [
        "docker", "exec", "-it", SOLR_CONTAINER,
        "bin/solr", "create_core", "-c", core_name
    ]
    run_command(cmd)



def copy_conf_files(core_name):
    for file_path in [SYNONYMS_FILE, STOPWORDS_FILE]:
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        cmd = [
            "docker", "cp",
            str(file_path),
            f"{SOLR_CONTAINER}:/var/solr/data/{core_name}/conf/"
        ]
        run_command(cmd)


def main():
    for core in CORES:
        print(f"🚀 Criar core '{core}'...")
        create_core(core)
        copy_conf_files(core)
        print(f"✅ Core '{core}' configurado!\n")


if __name__ == "__main__":
    main()
