#!/usr/bin/env python3
# Copyright 2026 Bob Bomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
studioctl - Studio cluster management utility
"""

import sys
import subprocess
import json
import base64
import secrets
import string
import argparse
from pathlib import Path
from typing import Optional

def run_kubectl(args: list[str], capture_output: bool = True) -> subprocess.CompletedProcess:
    """Run kubectl command and return result."""
    cmd = ["kubectl"] + args
    result = subprocess.run(cmd, capture_output=capture_output, text=True)
    return result

def get_secret_value(name: str, namespace: str, key: str) -> Optional[str]:
    """Get a value from a Kubernetes secret."""
    result = run_kubectl([
        "get", "secret", name,
        "-n", namespace,
        "-o", f"jsonpath={{.data['{key}']}}"
    ])
    if result.returncode != 0:
        return None
    return base64.b64decode(result.stdout).decode('utf-8')

def generate_password(length: int = 32) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

class DatabaseCommands:
    def __init__(self, cluster_name: str, namespace: str):
        self.cluster_name = cluster_name
        self.namespace = namespace

    def create(self, size: str = "10Gi", instances: int = 1):
        """Create a new CloudNativePG cluster."""
        manifest = f"""apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: {self.cluster_name}
  namespace: {self.namespace}
spec:
  instances: {instances}
  storage:
    size: {size}
  certificates:
    serverAltDNSNames:
      - {self.cluster_name}-rw.abode.tailandtraillabs.org
      - {self.cluster_name}-ro.abode.tailandtraillabs.org
      - {self.cluster_name}-r.abode.tailandtraillabs.org
"""
        proc = subprocess.Popen(
            ["kubectl", "apply", "-f", "-"],
            stdin=subprocess.PIPE,
            text=True
        )
        proc.communicate(input=manifest)
        
        if proc.returncode == 0:
            print(f"✓ Created cluster {self.cluster_name} in namespace {self.namespace}")
        else:
            print(f"✗ Failed to create cluster", file=sys.stderr)
            sys.exit(1)

    def edit(self):
        """Edit the cluster manifest."""
        result = run_kubectl([
            "edit", "cluster", self.cluster_name,
            "-n", self.namespace
        ], capture_output=False)
        if result.returncode != 0:
            print(f"✗ Failed to edit cluster", file=sys.stderr)
            sys.exit(1)

    def delete(self, force: bool = False):
        """Delete the cluster."""
        if not force:
            response = input(f"Delete cluster {self.cluster_name} in {self.namespace}? This will destroy all data. [yes/NO]: ")
            if response.lower() != "yes":
                print("Aborted.")
                return

        result = run_kubectl([
            "delete", "cluster", self.cluster_name,
            "-n", self.namespace
        ], capture_output=False)
        if result.returncode == 0:
            print(f"✓ Deleted cluster {self.cluster_name}")
        else:
            print(f"✗ Failed to delete cluster", file=sys.stderr)
            sys.exit(1)

    def createcert(self, target_namespace: str):
        """Copy CA certificate to target namespace."""
        # Get CA cert from CloudNativePG
        ca_cert = get_secret_value(f"{self.cluster_name}-ca", self.namespace, "ca.crt")
        if not ca_cert:
            print(f"✗ Failed to get CA cert from {self.namespace}/{self.cluster_name}-ca", file=sys.stderr)
            sys.exit(1)

        # Check if secret already exists
        check = run_kubectl([
            "get", "secret", f"{self.cluster_name}-ca",
            "-n", target_namespace
        ])
        if check.returncode == 0:
            print(f"✓ Secret {self.cluster_name}-ca already exists in {target_namespace}")
            return

        # Create secret in target namespace
        temp_file = Path(f"/tmp/{self.cluster_name}-ca.crt")
        temp_file.write_text(ca_cert)
        
        result = run_kubectl([
            "create", "secret", "generic", f"{self.cluster_name}-ca",
            f"--from-file=ca.crt={temp_file}",
            "-n", target_namespace
        ], capture_output=False)
        
        temp_file.unlink()
        
        if result.returncode == 0:
            print(f"✓ Created CA cert secret {self.cluster_name}-ca in {target_namespace}")
        else:
            print(f"✗ Failed to create cert secret", file=sys.stderr)
            sys.exit(1)

    def deletecert(self, target_namespace: str):
        """Delete CA certificate from target namespace."""
        result = run_kubectl([
            "delete", "secret", f"{self.cluster_name}-ca",
            "-n", target_namespace
        ], capture_output=False)
        if result.returncode == 0:
            print(f"✓ Deleted CA cert from {target_namespace}")
        else:
            print(f"✗ Failed to delete cert", file=sys.stderr)
            sys.exit(1)

    def createpassword(self, username: str = "app", database: str = "app"):
        """Display connection info including password."""
        password = get_secret_value(f"{self.cluster_name}-{username}", self.namespace, "password")
        if not password:
            print(f"✗ Failed to get password for user {username}", file=sys.stderr)
            sys.exit(1)

        print(f"\nConnection Info for {self.cluster_name}:")
        print(f"  Host (RW): {self.cluster_name}-rw.{self.namespace}.svc.cluster.local")
        print(f"  Host (RO): {self.cluster_name}-ro.{self.namespace}.svc.cluster.local")
        print(f"  Host (R):  {self.cluster_name}-r.{self.namespace}.svc.cluster.local")
        print(f"  Port:      5432")
        print(f"  Database:  {database}")
        print(f"  Username:  {username}")
        print(f"  Password:  {password}")
        print(f"\nExternal (via Traefik):")
        print(f"  Host (RW): {self.cluster_name}-rw.abode.tailandtraillabs.org")
        print(f"  Host (RO): {self.cluster_name}-ro.abode.tailandtraillabs.org")
        print(f"  Host (R):  {self.cluster_name}-r.abode.tailandtraillabs.org")
        print(f"\nConnection string:")
        print(f"  postgresql://{username}:{password}@{self.cluster_name}-rw.{self.namespace}.svc.cluster.local:5432/{database}?sslmode=require")

    def updatepassword(self, username: str = "app"):
        """Update password for a database user."""
        print("✗ Password updates not yet implemented", file=sys.stderr)
        print("CloudNativePG manages passwords automatically.", file=sys.stderr)
        print("To change password, recreate the cluster or use SQL ALTER USER.", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Studio cluster management utility')
    parser.add_argument('module', choices=['database'], help='Module to use')
    parser.add_argument('command', choices=['create', 'edit', 'delete', 'createcert', 'deletecert', 'createpassword', 'updatepassword'], 
                       help='Command to run')
    parser.add_argument('-c', '--cluster', default='studiodb', help='Cluster name (default: studiodb)')
    parser.add_argument('-n', '--namespace', default='cloudnative-pg', help='Source namespace where database lives (default: cloudnative-pg)')
    parser.add_argument('-t', '--target-namespace', help='Target namespace for cert operations')
    parser.add_argument('--force', action='store_true', help='Force delete without confirmation')
    parser.add_argument('--size', default='10Gi', help='Storage size for create (default: 10Gi)')
    parser.add_argument('--instances', type=int, default=1, help='Number of instances for create (default: 1)')
    
    args = parser.parse_args()

    db = DatabaseCommands(args.cluster, args.namespace)

    if args.command == "create":
        db.create(size=args.size, instances=args.instances)
    elif args.command == "edit":
        db.edit()
    elif args.command == "delete":
        db.delete(force=args.force)
    elif args.command == "createcert":
        if not args.target_namespace:
            print("Error: --target-namespace required for createcert")
            sys.exit(1)
        db.createcert(args.target_namespace)
    elif args.command == "deletecert":
        if not args.target_namespace:
            print("Error: --target-namespace required for deletecert")
            sys.exit(1)
        db.deletecert(args.target_namespace)
    elif args.command == "createpassword":
        db.createpassword()
    elif args.command == "updatepassword":
        db.updatepassword()

if __name__ == "__main__":
    main()
