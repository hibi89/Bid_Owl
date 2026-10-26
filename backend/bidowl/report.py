"""Offline, auditable PDF/XLSX exports from persisted assessment snapshots.

No customer data is transferred. No fonts are distributed with this module.
"""
from __future__ import annotations

import html
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from .store import BidOwlStore

REPORT_DISCLAIMER = (
    "자동 판정은 입력한 회사 정보와 공고 조건의 기계적 대조 결과입니다. "
    "법률·계약상 입찰 참가 자격을 보증하지 않으며 최종 판단은 담당자가 원문을 확인해야 합니다."
)


@dataclass(frozen=True)
class ReviewReport:
    assessment_id: int
    bid_no: str
    title: str
    agency: str
    category: str
    budget_krw: int
    source_id: str
    source_ref: str | None
    bid_version: int
    profile_id: str
    profile_version: int
    status: str
    checked_at: str
    bid_deadline: str
    data_as_of: str | None
    expired: bool
    requires_human_review: bool
    rules: tuple[dict[str, Any], ...]


def load_review_report(store: BidOwlStore, assessment_id: int) -> ReviewReport:
    """Never re-evaluate an assessment using changed profile/bid versions."""
    record = store.assessment(assessment_id)
    if record is None:
        raise KeyError(f"assessment {assessment_id} not found")
    assessment, rules = record
    bid = store.get_bid(assessment["source_id"], assessment["bid_no"], assessment["bid_version"])
    if bid is None:
        raise RuntimeError("referenced bid version not found")
    return ReviewReport(
        assessment_id=assessment["id"], bid_no=assessment["bid_no"], title=bid.title,
        agency=bid.agency, category=bid.category, budget_krw=bid.budget,
        source_id=assessment["source_id"], source_ref=bid.source_ref,
        bid_version=assessment["bid_version"], profile_id=assessment["profile_id"],
        profile_version=assessment["profile_version"], status=assessment["status"],
        checked_at=assessment["checked_at"], bid_deadline=bid.bid_deadline.isoformat(),
        data_as_of=assessment["data_as_of"], expired=bool(assessment["is_expired"]),
        requires_human_review=bool(assessment["requires_human_review"]),
        rules=tuple(dict(row) for row in rules),
    )


def _safe_string(value: Any) -> str:
    """Defuse Excel dynamic content and strip forbidden XML codepoints."""
    result = "" if value is None else str(value)
    result = "".join(ch for ch in result if ch in "\t\n\r" or (ord(ch) >= 32 and not 0xD800 <= ord(ch) <= 0xDFFF and ord(ch) not in (0xFFFE, 0xFFFF)))
    # XLSX cells can hold at most 32,767 characters. Refuse to lose evidence silently.
    if len(result) > 32767:
        raise ValueError("report cell exceeds Excel maximum size; cannot truncate source evidence")
    if re.match(r"^\s*[=+@\-\t\r\n]", result):
        return "'" + result
    return result


def _sheet_xml(rows: list[list[Any]]) -> bytes:
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    ET.register_namespace("", ns)
    root = ET.Element(f"{{{ns}}}worksheet")
    ET.SubElement(root, f"{{{ns}}}sheetViews")
    cols = ET.SubElement(root, f"{{{ns}}}cols")
    ET.SubElement(cols, f"{{{ns}}}col", {"min":"1","max":"1","width":"26","customWidth":"1"})
    ET.SubElement(cols, f"{{{ns}}}col", {"min":"2","max":"8","width":"35","customWidth":"1"})
    body = ET.SubElement(root, f"{{{ns}}}sheetData")
    for row_idx, values in enumerate(rows, 1):
        row_el = ET.SubElement(body, f"{{{ns}}}row", {"r":str(row_idx)})
        for col_idx, value in enumerate(values):
            if value is None:
                continue
            col = ""; k = col_idx + 1
            while k:
                k, remainder = divmod(k - 1, 26)
                col = chr(65 + remainder) + col
            attrs = {"r":f"{col}{row_idx}"}
            if row_idx == 1:
                attrs["s"] = "1"
            if type(value) in (int, float):
                cell = ET.SubElement(row_el, f"{{{ns}}}c", attrs)
                ET.SubElement(cell, f"{{{ns}}}v").text = str(value)
            else:
                cell = ET.SubElement(row_el, f"{{{ns}}}c", {**attrs,"t":"inlineStr"})
                text = ET.SubElement(ET.SubElement(cell, f"{{{ns}}}is"), f"{{{ns}}}t")
                text.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                text.text = _safe_string(value)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def write_xlsx(report: ReviewReport, destination: str | Path) -> Path:
    """OOXML inline strings prevent formula execution and remove Excel dependencies."""
    dest = Path(destination)
    dest.parent.mkdir(parents=True, exist_ok=True)
    summary = [
        ["항목", "값"], ["보고서 종류", "BID OWL | 입찰 검토 보고서"],
        ["분석 ID", report.assessment_id], ["회사 ID", report.profile_id],
        ["회사 프로필 버전", report.profile_version], ["공고번호", report.bid_no],
        ["공고 제목", report.title], ["발주기관", report.agency],
        ["분야", report.category], ["사업비(KRW)", report.budget_krw],
        ["데이터 소스", report.source_id], ["원문 참조", report.source_ref or "미기재"],
        ["공고 데이터 버전", report.bid_version], ["데이터 기준일", report.data_as_of or "미확인"],
        ["판정 시각", report.checked_at], ["접수 마감일", report.bid_deadline],
        ["마감 경과", "예" if report.expired else "아니오"],
        ["종합 판정", report.status],
        ["사람 검토 필요", "예" if report.requires_human_review else "아니오"],
        ["최종 승인", "담당자 직접 확인 필수"], ["고지", REPORT_DISCLAIMER],
    ]
    rule_rows = [["규칙 ID","유형","판정","사유 코드","판정 설명","원문 문구","원문 위치","사람 검토"]]
    for rule in report.rules:
        rule_rows.append([
            rule["rule_id"],rule["kind"],rule["status"],rule["reason_code"],
            rule["explanation"],rule["source_text"] or "미기재",rule["source_locator"] or "미기재",
            "예" if rule["requires_human_review"] else "아니오",
        ])
    if not report.rules:
        rule_rows.append(["없음","-","UNKNOWN","NO_RULES","자격조건 정보가 없어 검토가 필요합니다.","미기재","미기재","예"])
    types = "http://schemas.openxmlformats.org/package/2006/content-types"
    rels = "http://schemas.openxmlformats.org/package/2006/relationships"
    office_rels = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    main = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    ET.register_namespace("", main)
    workbook = ET.Element(f"{{{main}}}workbook")
    sheets = ET.SubElement(workbook, f"{{{main}}}sheets")
    ET.SubElement(sheets, f"{{{main}}}sheet", {"name":"검토요약","sheetId":"1",f"{{{office_rels}}}id":"rId1"})
    ET.SubElement(sheets, f"{{{main}}}sheet", {"name":"조건별근거","sheetId":"2",f"{{{office_rels}}}id":"rId2"})
    styles = b'''<?xml version="1.0" encoding="UTF-8"?>
    <styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
    <fonts count="2"><font><sz val="10"/><name val="Aptos"/></font><font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Aptos"/></font></fonts>
    <fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF263C58"/><bgColor indexed="64"/></patternFill></fill></fills>
    <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
    <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
    <cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/></cellXfs>
    </styleSheet>'''
    content_types = f'''<?xml version="1.0" encoding="UTF-8"?>
    <Types xmlns="{types}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
    <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
    <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
    <Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'''
    pkgrels = f'''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{rels}">
    <Relationship Id="rId1" Type="{office_rels}/officeDocument" Target="xl/workbook.xml"/></Relationships>'''
    bookrels = f'''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{rels}">
    <Relationship Id="rId1" Type="{office_rels}/worksheet" Target="worksheets/sheet1.xml"/>
    <Relationship Id="rId2" Type="{office_rels}/worksheet" Target="worksheets/sheet2.xml"/>
    <Relationship Id="rId3" Type="{office_rels}/styles" Target="styles.xml"/></Relationships>'''
    created = False
    try:
        with dest.open("xb") as stream:
            created = True  # Exclusive creation succeeded; only our file may be cleaned up.
            with ZipFile(stream, "w", ZIP_DEFLATED) as out:
                out.writestr("[Content_Types].xml", content_types)
                out.writestr("_rels/.rels", pkgrels)
                out.writestr("xl/workbook.xml", ET.tostring(workbook, encoding="utf-8", xml_declaration=True))
                out.writestr("xl/_rels/workbook.xml.rels", bookrels)
                out.writestr("xl/styles.xml", styles)
                out.writestr("xl/worksheets/sheet1.xml", _sheet_xml(summary))
                out.writestr("xl/worksheets/sheet2.xml", _sheet_xml(rule_rows))
    except BaseException:
        if created:
            dest.unlink(missing_ok=True)
        raise
    return dest


class KoreanFontUnavailable(RuntimeError):
    pass


def _korean_font_path() -> Path:
    candidates = [os.environ.get("BIDOWL_PDF_FONT"),
                  r"C:\Windows\Fonts\malgun.ttf",
                  "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                  "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf"]
    for candidate in candidates:
        if candidate and Path(candidate).is_file() and Path(candidate).suffix.lower() == ".ttf":
            return Path(candidate)
    raise KoreanFontUnavailable(
        "한국어 PDF용 TTF 글꼴을 찾을 수 없습니다. Windows 맑은 고딕 또는 설치된 나눔고딕을 사용하거나 BIDOWL_PDF_FONT로 로컬 TTF 경로를 지정하세요."
    )


def check_pdf_support() -> Path:
    try:
        import reportlab  # noqa: F401; optional report dependency
    except ImportError as exc:
        raise RuntimeError("PDF 생성에는 reportlab 패키지가 필요합니다: pip install reportlab>=4.2,<5") from exc
    return _korean_font_path()


def write_pdf(report: ReviewReport, destination: str | Path) -> Path:
    """Create Korean embedded-font PDF with proper paragraph wrapping and page breaks."""
    font_path = check_pdf_support()
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether

    font_name = "BidOwlKorean"
    if font_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
    body = ParagraphStyle("body", fontName=font_name, fontSize=8.9, leading=13.7, textColor=colors.HexColor("#223148"),spaceAfter=7,alignment=TA_LEFT,wordWrap="CJK")
    heading = ParagraphStyle("heading",parent=body,fontSize=15,leading=23,spaceBefore=3,spaceAfter=12)
    subheading = ParagraphStyle("subheading",parent=body,fontSize=11,leading=18,spaceBefore=9,spaceAfter=4)
    muted = ParagraphStyle("muted",parent=body,fontSize=8,leading=13,textColor=colors.HexColor("#51627B"))
    boldlabel = ParagraphStyle("label",parent=body,fontSize=8,leading=12,textColor=colors.HexColor("#243D59"))

    def p(value: object, style=body) -> Paragraph:
        return Paragraph(html.escape(str(value) if value is not None else "미기재"),style)

    dest = Path(destination)
    dest.parent.mkdir(parents=True,exist_ok=True)
    # Reserve target without overwriting any customer report; ReportLab opens by name.
    with dest.open("xb"):
        pass
    try:
        doc = SimpleDocTemplate(str(dest), pagesize=A4, rightMargin=16*mm,leftMargin=16*mm, topMargin=15*mm,bottomMargin=16*mm,
                                title=f"BID OWL 검토 보고서 - {report.bid_no}",author="BID OWL")
        elements = [p("BID OWL | 입찰 조건 검토 보고서", heading),
                    p("자동 판정 참고용 · 실제 참가 전 담당자 확인 필수",muted),
                    Spacer(1,2.8*mm)]
        entries = [
            ("회사 ID / 버전",f"{report.profile_id} / {report.profile_version}"),
            ("공고번호 / 버전",f"{report.bid_no} / {report.bid_version}"),
            ("공고명",report.title), ("발주기관",report.agency),
            ("분야",report.category),("사업비",f"{report.budget_krw:,} KRW"),
            ("종합 판정",report.status),("마감 경과","예" if report.expired else "아니오"),
            ("마감 일시",report.bid_deadline), ("평가 시각",report.checked_at),
            ("데이터 기준일",report.data_as_of or "미확인"),
            ("수집 출처",report.source_id),("원문 식별",report.source_ref or "미기재"),
            ("사람 검토 요청","예" if report.requires_human_review else "아니오"),
        ]
        t = Table([[p(k,boldlabel),p(v,body)] for k,v in entries], colWidths=[36*mm,142*mm],hAlign="LEFT")
        t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                               ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#E8EEF5")),
                               ("BOTTOMPADDING",(0,0),(-1,-1),3.3),
                               ("TOPPADDING",(0,0),(-1,-1),3.3),
                               ("LINEBELOW",(0,0),(-1,-1),0.25,colors.HexColor("#D9E1EA"))]))
        elements.extend([t,p("조건별 판정 근거",subheading)])
        if not report.rules:
            elements.append(p("조건 정보가 없어 UNKNOWN입니다. 원문 전체를 확인하세요."))
        for rule in report.rules:
            intro = f"{rule['rule_id']} · {rule['kind']} · {rule['status']} ({rule['reason_code']})"
            # table can split between rows, preventing multi-line row overflow at ordinary sizes
            details = Table([[p("사유",boldlabel),p(rule['explanation'])],
                             [p("원문",boldlabel),p(rule['source_text'] or "미기재")],
                             [p("위치",boldlabel),p(rule['source_locator'] or "미기재")],
                             [p("추가 검토",boldlabel),p("예" if rule['requires_human_review'] else "아니오")]],
                            colWidths=[24*mm,154*mm],hAlign="LEFT")
            details.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                         ("BOX",(0,0),(-1,-1),0.4,colors.HexColor("#D8E0E9")),
                                         ("TOPPADDING",(0,0),(-1,-1),3.5),
                                         ("BOTTOMPADDING",(0,0),(-1,-1),3.5)]))
            elements.extend([p(intro,subheading),details,Spacer(1,3*mm)])
        elements.extend([Spacer(1,2.8*mm),p("유의사항",subheading),p(REPORT_DISCLAIMER,muted)])

        def footer(canvas, document):
            canvas.setFont(font_name,8)
            canvas.setFillColor(colors.HexColor("#728197"))
            canvas.drawString(16*mm,10*mm,f"BID OWL · 검토 ID {report.assessment_id}")
            canvas.drawRightString(A4[0]-16*mm,10*mm,f"{document.page} 쪽")

        doc.build(elements,onFirstPage=footer,onLaterPages=footer)
    except BaseException:
        dest.unlink(missing_ok=True)
        raise
    return dest
