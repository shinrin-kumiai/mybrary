from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session

from src.dependencies import get_db, get_current_user, get_thumbnail_save_path
from src import crud, services, schemas

router = APIRouter(
    tags=['community']
)


@router.post("/community/create", response_model=schemas.CommunityInfo)
async def create_community(
    community_setup_info: schemas.CommunitySetupInfo,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> None:
    try:
        created_community_id = crud.create_new_community(
                db=db,
                user_id=user_id, 
                community_setup_info=community_setup_info
            )
        created_community = crud.search_community_by_id(
                db=db,
                community_id=created_community_id
            )
        return schemas.CommunityInfo.mapping_to_dict(target_community=created_community)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/communities/{community_id}/add/{target_user_id}")
async def add_community_member(
    community_id: str,
    target_user_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> dict:
    try:
        target_community = crud.search_community_by_id(
                    db=db,
                    community_id=community_id
                )
        if target_community.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="コミュニティに対してオーナー権限がありません."
            )
        if len(list(filter(lambda user: user.id == target_user_id, target_community.user))) != 0:
            raise HTTPException(
                status_code=400,
                detail="このユーザーは既にメンバー登録済みです."
            )
        crud.add_commynity_member(
            db=db,
            community_id=community_id,
            target_user_id=target_user_id,
        )
        target_user_info = crud.search_user_by_id(db=db, user_id=target_user_id)
        return {"message": f"{target_user_info.name}さんが{target_community.name}に参加しました！"}

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")