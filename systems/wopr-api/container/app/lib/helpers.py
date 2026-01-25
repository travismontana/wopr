import logging
import httpx

def setup_logging(name: str, level: str, file_path: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Create file handler
    fh = logging.FileHandler(file_path)
    fh.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

logger = setup_logging("wopr-api", "INFO", "/tmp/wopr-api.log")


def do_api_things(action, base_url, route, path, payload):
    headers = ""
    result = []
    logger.info(
        f"Doing API things - "
        f"Action: {action}, "
        f"Base URL: {base_url}, "
        f"Route: {route}, "
        f"Path: {path}, "
        f"Headers: {headers}, "
        f"Payload: {payload}"
    )

    action_map = {
        "get": httpx.get,
        "post": httpx.post,
        "put": httpx.put,
        "patch": httpx.patch,
        "delete": httpx.delete,
    }

    method = action_map[action.lower()]
    logger.info(f"Using HTTP method: {method.__name__}")

    timeout = 30.0
    parts = [base_url, route, path]
    url = "/".join(str(p).strip("/") for p in parts if p)
    logger.info(f"Constructed URL: {url}")

    # Build request kwargs based on HTTP method
    kwargs = {"timeout": 10.0, "headers": headers}

    if action.lower() in ["post", "put", "patch"] and payload:
        kwargs["json"] = payload
    elif action.lower() == "get" and payload:
        # If payload exists for GET, treat as query params
        kwargs["params"] = payload

    response = method(url, **kwargs)
    response.raise_for_status()
    # for item in response:
    #    result.append(item.json())
    result = response.json()
    logger.info(f"Response status code: {response}")
    logger.info(f"Response result: {result}")
    logger.debug(response.text)

    return result
