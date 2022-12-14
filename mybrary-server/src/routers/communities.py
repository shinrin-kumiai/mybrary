import os
import dotenv
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from functools import partial
from typing import List

from src.dependencies import get_db, get_current_user, get_thumbnail_save_path
from src import crud, services, schemas

router = APIRouter(
    tags=['communities']
)

dotenv.load_dotenv(override=True)


@router.post("/community/create", response_model=schemas.CommunityInfo)
async def create_community(
    community_setup_info: schemas.CommunitySetupInfo,
    token: str | None = Query(default=None, description="トークン"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> None:
    if os.environ.get("USE_HEADER") == "true":
        user_id = services.decode_token(token)
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
        crud.add_commynity_member(
            db=db,
            community_id=created_community_id,
            target_user_id=user_id,
        )
        return schemas.CommunityInfo.mapping_to_dict(
            target_community=created_community,
            user_id=user_id
        )
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/communities/{community_id}/add/{target_user_id}")
async def add_community_member(
    community_id: str,
    target_user_id: str,
    token: str | None = Query(default=None, description="トークン"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> dict:
    if os.environ.get("USE_HEADER") == "true":
        user_id = services.decode_token(token)
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


@router.get("/communities/{community_id}")
async def get_communitiy_info(
    community_id: str,
    token: str | None = Query(default=None, description="トークン"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    if os.environ.get("USE_HEADER") == "true":
        user_id = services.decode_token(token)
    try:
        target_community = crud.search_community_by_id(db=db, community_id=community_id)
        return schemas.CommunityInfo.mapping_to_dict(target_community=target_community, user_id=user_id)

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/communities/{community_id}/books", response_model=List[schemas.UserBookInfo])
async def get_community_accessible_books(
    community_id: str,
    token: str | None = Query(default=None, description="トークン"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    if os.environ.get("USE_HEADER") == "true":
        user_id = services.decode_token(token)

    target_community = crud.search_community_by_id(db=db, community_id=community_id)
    all_members = target_community.user

    all_member_ids = list(map(lambda x: x.id, all_members))
    if user_id not in all_member_ids:
        raise HTTPException(
            status_code=403,
            detail="このコミュニティに対してアクセス権限がありません."
        )

    all_user_books = []
    for user in all_members:
        all_user_books += user.user_book
    return list(map(partial(schemas.UserBookInfo.mapping_to_dict, user_id=user_id, db=db), all_user_books))


@router.get("/communities/{community_id}/members", response_model=List[schemas.UserInfo])
def get_all_members(
    community_id: str,
    token: str | None = Query(default=None, description="トークン"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    if os.environ.get("USE_HEADER") == "true":
        user_id = services.decode_token(token)
    try:
        target_community = crud.search_community_by_id(db=db, community_id=community_id)
        all_members = target_community.user

        all_member_ids = list(map(lambda x: x.id, all_members))
        if user_id not in all_member_ids:
            raise HTTPException(
                status_code=403,
                detail="このコミュニティに対してアクセス権限がありません."
        )
        return list(map(partial(schemas.UserInfo.mapping_to_dict, user_id=user_id), target_community.user))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)