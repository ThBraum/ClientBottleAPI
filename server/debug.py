if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server.__main__:app", host="0.0.0.0", port=7000)
