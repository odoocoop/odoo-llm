import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = "mail.message"

    def _format_message_qwen(self):
        """Format mail.message for Qwen API (OpenAI-compatible format)

        Returns:
            Dictionary in OpenAI/Qwen message format
        """
        self.ensure_one()

        # Map Odoo message types to Qwen roles
        role_mapping = {
            "user": "user",
            "assistant": "assistant",
            "system": "system",
        }

        # Get the role based on message type or author
        if self.message_type == "notification":
            role = "assistant"
        elif self.author_id:
            role = "user"
        else:
            role = "assistant"

        # Override with explicit role if set
        if self.model == "llm.thread" and hasattr(self, "role"):
            role = role_mapping.get(self.role, role)

        # Build content - handle both text and attachments
        content = self.body or ""

        # If there are attachments, we could include them as multi-modal content
        # For now, just use text content
        return {"role": role, "content": content}
