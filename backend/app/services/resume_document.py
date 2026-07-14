"""Рендерит резюме в ATS-friendly PDF и DOCX."""

from html import escape
from io import BytesIO
from typing import Any, cast

from docx import Document
from docx.shared import Pt


class ResumeDocumentRenderer:
    """Рендерит единый шаблон резюме в поддерживаемые форматы."""

    def render_pdf(self, resume: Any) -> bytes:
        """Возвращает PDF представление резюме."""
        from weasyprint import HTML  # type: ignore[import-untyped]

        return cast(bytes, HTML(string=self._render_html(resume)).write_pdf())

    def render_docx(self, resume: Any) -> bytes:
        """Возвращает DOCX представление резюме."""
        document = Document()
        document.styles["Normal"].font.name = "Arial"
        document.styles["Normal"].font.size = Pt(10)
        document.add_heading(resume.title, level=0)
        for section in resume.sections:
            section_type = str(section.section_type)
            content = section.content
            if section_type == "summary":
                document.add_heading("Summary", level=1)
                document.add_paragraph(content["text"])
            elif section_type == "experience":
                document.add_heading("Experience", level=1)
                for item in content["experiences"]:
                    document.add_heading(
                        f"{item['position']} — {item['company']}", level=2
                    )
                    document.add_paragraph(self._period(item))
                    if item.get("description"):
                        document.add_paragraph(item["description"])
            elif section_type == "skills":
                document.add_heading("Skills", level=1)
                skills = ", ".join(
                    self._skill_label(item) for item in content["skills"]
                )
                document.add_paragraph(skills)
        stream = BytesIO()
        document.save(stream)
        return stream.getvalue()

    def _render_html(self, resume: Any) -> str:
        """Строит HTML единого шаблона."""
        content = self.render_docx(resume)
        document = Document(BytesIO(content))
        paragraphs = "".join(
            f"<p>{escape(paragraph.text)}</p>" for paragraph in document.paragraphs
        )
        return (
            "<html><head><meta charset='utf-8'><style>"
            "body{font-family:Arial,sans-serif;font-size:11pt;color:#111}"
            "h1{font-size:22pt}h2{font-size:15pt;margin-top:18pt}"
            "h3{font-size:12pt;margin-bottom:0}</style></head><body>"
            f"{paragraphs}</body></html>"
        )

    @staticmethod
    def _period(item: dict[str, Any]) -> str:
        """Форматирует период работы."""
        end_date = item.get("end_date") or "Present"
        return f"{item['start_date']} — {end_date}"

    @staticmethod
    def _skill_label(item: dict[str, Any]) -> str:
        """Форматирует навык."""
        level = item.get("level")
        return f"{item['name']} ({level})" if level else item["name"]
