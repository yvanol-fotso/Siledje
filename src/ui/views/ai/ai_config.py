"""
Modele de configuration IA.
"""

class AIConfig:
    """Modele de configuration IA."""
    
    def __init__(self):
        self.api_key = ""
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.7
        self.max_tokens = 2000
        self.top_p = 1.0
        self.frequency_penalty = 0.0
        self.presence_penalty = 0.0
        self.enabled = False
        self.auto_suggestions = True
        self.context_window = 4096

    def to_dict(self):
        return {
            'api_key': self.api_key,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'enabled': self.enabled,
            'auto_suggestions': self.auto_suggestions,
            'context_window': self.context_window,
        }

    def from_dict(self, data):
        self.api_key = data.get('api_key', '')
        self.model = data.get('model', 'gpt-3.5-turbo')
        self.temperature = data.get('temperature', 0.7)
        self.max_tokens = data.get('max_tokens', 2000)
        self.top_p = data.get('top_p', 1.0)
        self.frequency_penalty = data.get('frequency_penalty', 0.0)
        self.presence_penalty = data.get('presence_penalty', 0.0)
        self.enabled = data.get('enabled', False)
        self.auto_suggestions = data.get('auto_suggestions', True)
        self.context_window = data.get('context_window', 4096)