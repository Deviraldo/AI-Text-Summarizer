import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing from .env")


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="AI Text Summarizer",
    description="AI Text Summarization API using FastAPI, LangChain and Gemini",
    version="1.0.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Gemini model
# --------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3,
)


# --------------------------------------------------
# LangChain prompt
# --------------------------------------------------

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert text summarization assistant.

Summarize the user's text clearly and accurately.

Rules:
- Keep the important information.
- Remove unnecessary repetition.
- Do not add information that is not present.
- Use simple and easy-to-understand language.
- Return only the summary.
"""
        ),
        (
            "human",
            """
Summarize the following text:

{text}
"""
        ),
    ]
)


# --------------------------------------------------
# LangChain chain
# --------------------------------------------------

summarization_chain = prompt | llm


# --------------------------------------------------
# Request schema
# --------------------------------------------------

class SummarizeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=20,
        max_length=20000
    )


# --------------------------------------------------
# Response schema
# --------------------------------------------------

class SummarizeResponse(BaseModel):
    summary: str


# --------------------------------------------------
# Root endpoint
# --------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "AI Text Summarizer API is running"
    }


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


# --------------------------------------------------
# Summarization endpoint
# --------------------------------------------------

@app.post(
    "/summarize",
    response_model=SummarizeResponse
)
async def summarize(request: SummarizeRequest):

    try:

        # Call LangChain chain
        response = await summarization_chain.ainvoke(
            {
                "text": request.text
            }
        )

        summary = response.content

        # Gemini can theoretically return structured content,
        # so make sure we always return a string.
        if isinstance(summary, list):
            summary = " ".join(
                str(item) for item in summary
            )

        return SummarizeResponse(
            summary=str(summary)
        )

    except Exception as e:

        print("ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail="Failed to generate summary."
        )