"""Run a client probe against published Linux CE1.11.0 and disposable Neo4j.

Requires Docker and the Python neo4j package. Client arguments may contain
{endpoint} and {root}. Only the uniquely created container/temp directory is used.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import tarfile
import tempfile
import time
import urllib.request
import uuid
from neo4j import GraphDatabase


def eventually(action, timeout=90):
    deadline=time.monotonic()+timeout
    while True:
        try: return action()
        except Exception:
            if time.monotonic()>=deadline: raise
            time.sleep(1)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("client", nargs=argparse.REMAINDER)
    args=parser.parse_args()
    assert args.client,"provide a built client probe command"
    root="/ce-sdk-inventory"
    folder=Path(tempfile.mkdtemp(prefix="kumiho-sdk-inventory-"))
    asset="kumiho-server-linux-x86_64-v1.11.0.tar.gz"
    base="https://github.com/KumihoIO/kumiho-server-community/releases/download/v1.11.0/"
    checks=urllib.request.urlopen(base+"checksums.txt",timeout=30).read().decode("utf-8-sig")
    digest=next(line.split()[0] for line in checks.splitlines() if line.split()[-1]==asset)
    archive=folder/asset
    urllib.request.urlretrieve(base+asset,archive)
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==digest
    with tarfile.open(archive) as package: package.extractall(folder,filter="data")
    binary=next(folder.rglob("kumiho_server")); binary.chmod(0o700)
    container="sdk-inventory-"+uuid.uuid4().hex
    created=False; server=None; driver=None
    def docker(*command):
        return subprocess.run(["docker",*command],capture_output=True,text=True,check=True,timeout=90).stdout.strip()
    try:
        docker("run","-d","--name",container,"-p","127.0.0.1::7687","-e","NEO4J_AUTH=none","neo4j:5")
        created=True
        address=docker("port",container,"7687/tcp")
        assert address.startswith("127.0.0.1:")
        bolt_port=int(address.rsplit(":",1)[1])
        driver=GraphDatabase.driver(f"bolt://127.0.0.1:{bolt_port}",auth=("neo4j","unused"),connection_timeout=2,connection_acquisition_timeout=3)
        eventually(driver.verify_connectivity)
        with socket.socket() as probe:
            probe.bind(("127.0.0.1",0)); api_port=probe.getsockname()[1]
        config=folder/"ce.toml"
        config.write_text("\n".join(['eula_accepted=true','eula_version="1.1"','db_uri=""',f'neo4j_port={bolt_port}',
            'db_name="neo4j"','db_user="neo4j"','db_pass="unused"',f'server_addr="127.0.0.1:{api_port}"']),encoding="utf-8")
        env={k:v for k,v in os.environ.items() if not k.startswith("KUMIHO_")}
        env.update(KUMIHO_CONFIG=str(config),UPSTASH_REDIS_URL="",KUMIHO_EVENT_USAGE_REDIS_URL="",RUST_LOG="warn")
        with (folder/"ce.log").open("w") as log:
            server=subprocess.Popen([str(binary)],cwd=folder,env=env,stdout=log,stderr=subprocess.STDOUT)
            def live():
                assert server.poll() is None,"CE exited"
                with urllib.request.urlopen(f"http://127.0.0.1:{api_port}/api/_live",timeout=3) as response:
                    data=json.load(response); assert data["version"]=="1.11.0" and data["deployment_mode"]=="self_hosted_ce"
            eventually(live)
            with driver.session(database="neo4j") as session:
                session.run("MERGE (t:Tenant {tenant_id:'self-hosted-ce'}) CREATE (t)-[:OWNS]->(p:Project {tenant_id:'self-hosted-ce',project_id:'ce-sdk-inventory',name:'ce-sdk-inventory',allow_public:false}) CREATE (p)-[:CONTAINS]->(:Space {tenant_id:'self-hosted-ce',path:$root})",root=root).consume()
                session.run("MATCH (r:Space {tenant_id:'self-hosted-ce',path:$root}) UNWIND range(0,1003) AS n CREATE (r)-[:CONTAINS]->(:Space {tenant_id:'self-hosted-ce',path:$root+'/space'+toString(n)}) CREATE (r)-[:CONTAINS]->(:Item {tenant_id:'self-hosted-ce',kref:'kref://ce-sdk-inventory/item'+toString(n)+'.note',item_name:'item'+toString(n),kind:'note',deprecated:n=1003})",root=root).consume()
                session.run("MATCH (i:Item {tenant_id:'self-hosted-ce',item_name:'item0'}) SET i.item_name='.hidden',i.kref='kref://ce-sdk-inventory/.hidden.fact',i.kind='fact',i.hidden='true'").consume()
            command=[part.replace("{endpoint}",f"127.0.0.1:{api_port}").replace("{root}",root) for part in args.client]
            probe_env={k:v for k,v in os.environ.items() if not k.startswith("KUMIHO_")}
            probe_env["KUMIHO_CONFIG_DIR"]=str(folder/"empty-auth")
            subprocess.run(command,env=probe_env,check=True,timeout=180)
            print(json.dumps({"server":"published CE1.11.0","archive_sha256":digest,"spaces":1004,"items":1004,"result":"PASS"}))
    finally:
        if server and server.poll() is None:
            server.terminate()
            try: server.wait(timeout=15)
            except subprocess.TimeoutExpired: server.kill(); server.wait(timeout=5)
        if driver: driver.close()
        if created: docker("rm","-f","-v",container)
        print("Isolated test evidence: "+str(folder))


if __name__=="__main__": main()
