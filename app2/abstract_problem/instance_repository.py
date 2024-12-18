from typing import Type, TypeVar, Generic
from pydantic import BaseModel
import lzma

from .problem_info import ProblemInfo

# Define a generic type variable for the instance model
T = TypeVar('T', bound=BaseModel)

def check_instance_uid(instance_uid: str, fail: bool = True) -> bool:
    """
    Check if the instance_uid is valid. They are only allowed to contain alphanumeric characters, dashes, and underscores, and slashes for subdirectories. They are not allowed to start or end with a slash.
    """
    if (
        not all(c.isalnum() or c in "-_/" for c in instance_uid)
        or instance_uid.startswith("/")
        or instance_uid.endswith("/")
    ):
        if not fail:
            return False
        raise ValueError(
            "The instance_uid can only contain alphanumeric characters, dashes, and underscores, and slashes for subdirectories."
        )
    return True

class InstanceRepository(Generic[T]):
    """
    This class manages the file based instance storage.
    Note that this may be replaced by a cloud storage or a database later.
    """

    def __init__(self, problem_info: ProblemInfo):
        self.problem_info = problem_info
        self.instance_model: Type[T] = problem_info.instance_model # type: ignore



    def read_instance(self, instance_uid: str) -> T:
        """
        Get the instance with the given instance_uid.
        It will be in problem_info.path/instances/instance_uid.json.xz
        Returns the instance as a Pydantic model.
        """
        check_instance_uid(instance_uid)
        instance_path = self.problem_info.path / "instances" / f"{instance_uid}.json.xz"
        if not instance_path.exists():
            raise KeyError(f"No instance found with the uid {instance_uid}")
        with lzma.open(instance_path, "rt") as file:
            instance = self.instance_model.model_validate_json(file.read())
            if getattr(instance, self.problem_info.uid_attribute) != instance_uid:
                raise ValueError(
                    f"The instance_uid of the instance {instance_uid} does not match the file name"
                )
            return instance

    def write_instance(self, instance: T, overwrite: bool = False):
        """
        Write the instance to the file system.
        """
        if not isinstance(instance, self.instance_model):
            raise ValueError("The instance is not of the correct type")
        instance_uid = getattr(instance, self.problem_info.uid_attribute)
        check_instance_uid(instance_uid)
        instance_path = self.problem_info.path / "instances" / f"{instance_uid}.json.xz"
        if instance_path.exists() and not overwrite:
            raise ValueError(f"An instance with the uid {instance_uid} already exists")
        instance_path.parent.mkdir(parents=True, exist_ok=True)
        with lzma.open(instance_path, "wt") as file:
            file.write(instance.model_dump_json())

    def delete_instance(self, instance_uid: str):
        """
        Delete the instance with the given instance_uid.
        """
        check_instance_uid(instance_uid)
        instance_path = self.problem_info.path / "instances" / f"{instance_uid}.json.xz"
        if instance_path.exists():
            instance_path.unlink()

    def get_all_instance_uids(self) -> list[str]:
        """
        Get the unique identifiers of all instances.
        Iterate over the files in problem_info.path/instances and return the instance_uids.
        """
        instance_dir = self.problem_info.path / "instances"
        if not instance_dir.exists():
            return []
        suffix = ".json.xz"
        uids = [
            str(f.relative_to(instance_dir))[: -len(suffix)]
            for f in instance_dir.iterdir()
            if f.is_file() and str(f).endswith(suffix)
        ]
        # filter out invalid instance uids
        uids = [uid for uid in uids if check_instance_uid(uid, fail=False)]
        return uids
