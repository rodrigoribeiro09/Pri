import subprocess

SOLR_CONTAINER = "song_solr"

CORES = {
    "simple": "/dataset/dataset.csv",
    "songs": "/dataset/dataset.csv",
    "boosted": "/dataset/boosted.json",   
}

def run_command(cmd):
    print(f"> {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")

def post_docs():
    for core, path in CORES.items():
        print(f"🚀 Adicionar docs '{core}'...")
        cmd = [
            "docker", "exec", "-it", SOLR_CONTAINER,
            "sh", "-c", f"bin/solr post -c {core} {path}"
        ]
        run_command(cmd)
        print(f"✅ Docs enviados '{core}'\n")

if __name__ == "__main__":
    post_docs()
