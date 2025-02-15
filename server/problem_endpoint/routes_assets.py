from .security import verify_api_key


from .asset_repository import AssetRepository
from .problem_info import ProblemInfo
from fastapi import APIRouter, Depends


def build_asset_routes(
    router: APIRouter, problem_info: ProblemInfo, asset_repository: AssetRepository
):
    @router.post("/assets/{asset_class}/{instance_uid}")
    def add_asset(
        asset_class: str,
        instance_uid: str,
        asset: bytes,
        api_key: str = Depends(verify_api_key),
    ):
        """
        Add an asset for a specific instance.

        Parameters:
        - asset_class: The type of asset (e.g., 'image', 'thumbnail').
        - instance_uid: The unique identifier of the instance.
        - asset: The binary content of the asset to store.
        """
        asset_repository.add(asset_class, instance_uid, asset)

    @router.get("/assets/{instance_uid}", response_model=dict[str, str])
    def get_assets(instance_uid: str):
        """
        Retrieve all assets associated with a specific instance.

        The keys in the response represent asset classes, and the values represent the corresponding file paths.
        """
        available = asset_repository.available_assets_for_instance(instance_uid)
        return {
            asset_class: f"{problem_info.assets_url_root}{path}"
            for asset_class, path in available.items()
        }

    @router.delete("/assets/{asset_class}/{instance_uid}")
    def delete_assets(
        asset_class: str,
        instance_uid: str,
        api_key: str = Depends(verify_api_key),
    ):
        """
        Delete a specific asset for an instance.

        Example:
        To delete a thumbnail for an instance:
        /assets/thumbnail/instance123
        """
        asset_repository.delete_assets(instance_uid, asset_class=asset_class)
