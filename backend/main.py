from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.merge import router as merge_router
from app.routes.extract import router as extract_router
from app.routes.search import router as search_router
from app.routes.compress import router as compress_router
from app.routes.convert import router as convert_router
from app.routes.editor import router as editor_router
from app.routes.image_to_pdf import router as image_to_pdf_router


app = FastAPI(
    title="PDF Handler API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "PDF Handler Backend Running"
    }


app.include_router(merge_router)
app.include_router(extract_router)
app.include_router(search_router)
app.include_router(compress_router)
app.include_router(convert_router)
app.include_router(editor_router)
app.include_router(
    image_to_pdf_router,
    prefix="/convert"
)