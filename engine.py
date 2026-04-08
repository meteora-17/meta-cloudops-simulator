import uuid
from typing import Dict, List, Any

class CloudOpsEngine:
    def __init__(self):
        self.reset()

    def reset(self):
        self.resources = {"instances": [], "buckets": []}
        self.history = []
        self.task_states = {
            "task_1": {"provisioned": False},
            "task_2": {"bucket_created": False, "file_uploaded": False},
            "task_3": {"instance_created": False, "bucket_created": False}
        }
        return {"status": "reset", "message": "Environment initialized and resources cleared."}

    def get_state(self):
        return {"resources": self.resources, "task_progress": self.task_states}

    def step(self, action: str, params: Dict[str, Any]):
        result = {"status": "success", "message": ""}
        
        if action == "create_instance":
            name, instance_type, region = params.get("name"), params.get("type"), params.get("region")
            if not all([name, instance_type, region]):
                return {"status": "error", "message": "Validation Failed: Missing required parameters (name, type, region)."}
            if any(i['name'] == name for i in self.resources["instances"]):
                return {"status": "error", "message": f"Conflict: Instance with name '{name}' already exists."}

            instance = {"id": str(uuid.uuid4())[:8], "name": name, "type": instance_type, "region": region, "status": "running"}
            self.resources["instances"].append(instance)
            result["message"] = f"Success: Instance '{name}' (ID: {instance['id']}) provisioned in {region}."
            
            if name == "web-server" and instance_type == "t3.micro" and region == "us-east-1":
                self.task_states["task_1"]["provisioned"] = True
            if name == "db-prod" and instance_type == "m5.large":
                self.task_states["task_3"]["instance_created"] = True

        elif action == "delete_instance":
            name = params.get("name")
            original_len = len(self.resources["instances"])
            self.resources["instances"] = [i for i in self.resources["instances"] if i['name'] != name]
            if len(self.resources["instances"]) == original_len:
                return {"status": "error", "message": f"Not Found: No instance named '{name}' to delete."}
            result["message"] = f"Success: Instance '{name}' terminated."

        elif action == "create_bucket":
            name = params.get("name")
            if not name: return {"status": "error", "message": "Validation Failed: Bucket name is required."}
            if any(b['name'] == name for b in self.resources["buckets"]):
                 return {"status": "error", "message": f"Conflict: Bucket '{name}' already exists globally."}

            bucket = {"name": name, "files": []}
            self.resources["buckets"].append(bucket)
            result["message"] = f"Success: S3-Compatible bucket '{name}' created."
            if name == "company-reports": self.task_states["task_2"]["bucket_created"] = True
            if name == "db-backups": self.task_states["task_3"]["bucket_created"] = True

        elif action == "upload_file":
            bucket_name, filename, content = params.get("bucket"), params.get("name"), params.get("content")
            bucket = next((b for b in self.resources["buckets"] if b["name"] == bucket_name), None)
            if not bucket: return {"status": "error", "message": f"Access Denied: Bucket '{bucket_name}' does not exist."}
            
            bucket["files"].append({"name": filename, "content": content})
            result["message"] = f"Success: File '{filename}' synced to '{bucket_name}'."
            if bucket_name == "company-reports" and filename == "policy.txt" and content == "confidential-data":
                self.task_states["task_2"]["file_uploaded"] = True
        else:
            return {"status": "error", "message": f"Unknown Action: The command '{action}' is not supported by the CloudOps API."}

        self.history.append({"action": action, "params": params, "result": result})
        return result

    def calculate_reward(self, task_id: str) -> float:
        if task_id == "task_1": return 1.0 if self.task_states["task_1"]["provisioned"] else 0.0
        elif task_id == "task_2":
            score = 0.0
            if self.task_states["task_2"]["bucket_created"]: score += 0.5
            if self.task_states["task_2"]["file_uploaded"]: score += 0.5
            return score
        elif task_id == "task_3":
            score = 0.0
            if self.task_states["task_3"]["instance_created"]: score += 0.5
            if self.task_states["task_3"]["bucket_created"]: score += 0.5
            return score
        return 0.0
