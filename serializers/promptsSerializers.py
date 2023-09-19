def promptEntity(prompt) -> dict:
    _id = str(prompt["_id"])
    del prompt["_id"]
    prompt["_id"] = _id
    return prompt


def promptsEntity(prompts):
    return [promptEntity(prompt) for prompt in prompts]
