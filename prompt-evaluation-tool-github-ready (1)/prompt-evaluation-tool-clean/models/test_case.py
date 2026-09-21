class TestCase:
    def __init__(self, name, prompt, question, expected_behavior="auto"):
        self.name = name
        self.prompt = prompt
        self.question = question
        # "auto" = infer from prompt + question; no manual selection needed
        self.expected_behavior = expected_behavior