#!/usr/bin/env python3
import subprocess

# Configurações
SOLR_CONTAINER = "song_solr"
CORES = ["simple", "songs", "songsBoost"] 
DATASET_FILE = "/data/dataset.csv"  

def run_command(cmd):
    print(f"> {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")

def post_docs():
    for core in CORES:
        print(f"🚀 Adicionar docs'{core}'...")
        cmd = [
            "docker", "exec", "-it", SOLR_CONTAINER,
            "sh", "-c", f"bin/solr post -c {core} {DATASET_FILE}"
        ]
        run_command(cmd)
        print(f"✅ Docs enviados '{core}'\n")

if __name__ == "__main__":
    post_docs()
