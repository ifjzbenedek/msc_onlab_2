from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import config
from src.api.schemas.ask_request import AskRequest
from src.pipeline.baseline import answer_question
from src.pipeline.schemas.answer import Answer

app = FastAPI()


@app.post("/ask")
def ask(ask_request: AskRequest) -> Answer:
    return answer_question(ask_request.question)


app.mount("/", StaticFiles(directory=config.WEB_DIR, html=True, check_dir=False))
