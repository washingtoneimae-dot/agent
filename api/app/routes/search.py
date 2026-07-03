from fastapi import APIRouter, Query, Depends
from sqlalchemy import select, desc, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.file import File, FileStatus
from app.models.user import User
from app.services.search import detect_query_depth

router = APIRouter()


@router.get("/search")
async def search(q: str = Query(..., min_length=1, max_length=200), limit: int = Query(3, ge=1, le=10),
                db: AsyncSession = Depends(get_db)):
    query = q.strip().lower()

    try:
        tsquery_parts = [f"{w}:*" for w in query.split() if len(w) > 1]
        tsquery = " & ".join(tsquery_parts) if tsquery_parts else query
        result = await db.execute(
            select(File).where(File.status == FileStatus.ACTIVE).where(
                text("to_tsvector('english', coalesce(title,'') || ' ' || coalesce(description,'') || ' ' || coalesce(tags,'')) @@ to_tsquery('english', :q)")
            ).params(q=tsquery).order_by(desc(File.score)).limit(10))
        files = result.scalars().all()

        if not files:
            for word in query.split():
                if len(word) <= 2:
                    continue
                r = await db.execute(
                    select(File).where(File.status == FileStatus.ACTIVE).where(
                        text("lower(title) like :w or lower(description) like :w or lower(tags) like :w")
                    ).params(w=f"%{word}%").order_by(desc(File.score)).limit(10))
                files = r.scalars().all()
                if files:
                    break
    except Exception:
        files = []

    if not files:
        return {"query": query, "query_depth": "broad", "results": []}

    enriched = []
    for f in files:
        u = (await db.execute(select(User).where(User.id == f.contributor_id))).scalar_one_or_none()
        enriched.append({"id": f.id, "title": f.title,
                         "description": f.description[:200] + ("..." if len(f.description) > 200 else ""),
                         "score": f.score, "download_count": f.download_count,
                         "extraction_count": f.extraction_count, "children_count": f.children_count,
                         "parent_id": f.parent_id, "category": f.category.value if hasattr(f.category, 'value') else str(f.category),
                         "contributor_name": u.display_name if u else None})

    depth = detect_query_depth(query)
    shaped = []
    for item in enriched[:limit]:
        s = dict(item)
        if depth == "broad" and item["children_count"] > 0:
            cr = (await db.execute(select(File).where(File.parent_id == item["id"], File.status == FileStatus.ACTIVE).order_by(desc(File.extraction_count)).limit(3))).scalars().all()
            s["children"] = [{"id": c.id, "title": c.title, "extraction_count": c.extraction_count} for c in cr]
        elif depth == "moderate" and item["parent_id"]:
            p = await db.get(File, item["parent_id"])
            if p:
                s["parent"] = {"id": p.id, "title": p.title}
            sr = (await db.execute(select(File).where(File.parent_id == item["parent_id"], File.status == FileStatus.ACTIVE, File.id != item["id"]).order_by(desc(File.extraction_count)).limit(3))).scalars().all()
            s["siblings"] = [{"id": c.id, "title": c.title, "extraction_count": c.extraction_count} for c in sr]
        elif depth == "specific":
            path, cid = [], item["parent_id"]
            while cid:
                p = await db.get(File, cid)
                if p:
                    path.insert(0, {"id": p.id, "title": p.title})
                    cid = p.parent_id
                else:
                    break
            s["parent_path"] = path
        shaped.append(s)

    return {"query": query, "query_depth": depth, "results": shaped}
