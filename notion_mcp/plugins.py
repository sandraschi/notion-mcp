import os
import importlib.util
import structlog
from typing import List, Dict, Any

logger = structlog.get_logger(__name__)


class PluginManager:
    """
    Manages NotionMCP plugins with SOTA efficiency.
    Plugins are loaded dynamically from the plugins/ directory.
    """

    def __init__(self, plugins_dir: str = "./plugins"):
        self.plugins_dir = plugins_dir
        self.plugins = {}
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
            logger.info("Created plugins directory", path=self.plugins_dir)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all installed and available plugins."""
        # For now, return a mix of installed and 'market' suggestions
        installed = []
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                plugin_name = filename[:-3]
                installed.append(
                    {
                        "name": plugin_name,
                        "id": plugin_name,
                        "status": "installed",
                        "description": f"Local plugin: {plugin_name}",
                        "author": "Local User",
                    }
                )

        # SOTA Marketplace Suggestions
        suggestions = [
            {
                "id": "slack_sync",
                "name": "Slack Intelligent Sync",
                "description": "Bi-directional Slack thread to Notion sync",
                "status": "available",
                "author": "SOTA Labs",
            },
            {
                "id": "gcal_bridge",
                "name": "Google Calendar Bridge",
                "description": "Two-way calendar event synchronization",
                "status": "available",
                "author": "Sandra (Vienna)",
            },
            {
                "id": "github_actions",
                "name": "GitHub Actions Reporter",
                "description": "Feed build status to Notion databases",
                "status": "available",
                "author": "Sandra (Vienna)",
            },
        ]

        return installed + suggestions

    def load_plugins(self):
        """Dynamically load plugins into memory."""
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                self.load_plugin(filename[:-3])

    def load_plugin(self, name: str):
        """Load a specific plugin."""
        try:
            path = os.path.join(self.plugins_dir, f"{name}.py")
            spec = importlib.util.spec_from_file_location(name, path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.plugins[name] = module
                logger.info("Plugin loaded", plugin=name)
        except Exception as e:
            logger.error("Failed to load plugin", plugin=name, error=str(e))
