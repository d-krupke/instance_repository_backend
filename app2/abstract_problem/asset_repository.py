
from pathlib import Path
from .instance_repository import check_instance_uid
from .problem_info import ProblemInfo


class AssetRepository:
    def __init__(self, problem_info: ProblemInfo):
        self.problem_info = problem_info

    def add(self, asset_class, instance_uid, asset,  exists_ok: bool = False) -> Path:
        """
        Add a binary asset to the repository.
        """
        check_instance_uid(instance_uid)
        extension = self.problem_info.assets[asset_class]
        asset_path = self.problem_info.path / "assets" / asset_class / f"{instance_uid}.{extension}"
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        if asset_path.exists() and not exists_ok:
            raise ValueError(f"An asset with the uid {instance_uid} already exists")
        with open(asset_path, "wb") as file:
            file.write(asset)
        return asset_path
    
    def delete_assets(self, instance_uid: str):
        """
        Delete the assets with the given instance_uid.
        """
        check_instance_uid(instance_uid)
        asset_dir = self.problem_info.path / "assets"
        if not asset_dir.exists():
            return
        for asset_class, extension in self.problem_info.assets.items():
            asset_path = asset_dir / asset_class / f"{instance_uid}.{extension}"
            if asset_path.exists():
                asset_path.unlink()