"""Create new cover and a multi-agent PDF with generated table of contents."""
from pathlib import Path
import importlib.util
import json
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Spacer, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader

HERE=Path(__file__).resolve().parent
STEM='project01_CT_04_HieuGM.299'
spec=importlib.util.spec_from_file_location('format_pdf',HERE/'pdf-format.py')
fmt=importlib.util.module_from_spec(spec);spec.loader.exec_module(fmt)
WIDTH,HEIGHT=A4


def cover(canvas):
    canvas.saveState()
    canvas.setStrokeColorRGB(0,0,0);canvas.setLineWidth(1)
    canvas.rect(36,35,WIDTH-72,HEIGHT-70)
    canvas.setLineWidth(.45);canvas.rect(40,39,WIDTH-80,HEIGHT-78)
    def line(text,y,size=13,bold=False):
        canvas.setFont('Times-Bold' if bold else 'Times',size)
        canvas.drawCentredString(WIDTH/2,y,text)
    line('HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG',774,13,True)
    line('KHOA CÔNG NGHỆ THÔNG TIN 1',744,13,True)
    logo=HERE/'assets/ptit-logo.png'
    canvas.drawImage(ImageReader(str(logo)),WIDTH/2-38,602,width=76,height=94,preserveAspectRatio=True,mask='auto')
    line('BÁO CÁO PROJECT 01',559,21,True)
    line('PHÁT TRIỂN HỆ THỐNG THÔNG MINH',524,19,True)
    line('ĐỀ TÀI',472,14,True)
    line('HỆ ĐA AGENT HỖ TRỢ',437,15,True)
    line('BỆNH ĐÁI THÁO ĐƯỜNG',412,15,True)
    line('DEEP LEARNING - KNOWLEDGE BASE - RAG',387,15,True)
    canvas.setFont('Times-Italic',12)
    canvas.drawCentredString(WIDTH/2,353,'Dữ liệu thật, mô hình đã huấn luyện và demo triển khai')
    config=json.loads((HERE/'cover-info.json').read_text(encoding='utf-8'))
    for i,(label,value) in enumerate(config.items()):
        y=296-i*23
        canvas.setFont('Times-Bold',12);canvas.drawString(120,y,label+':')
        canvas.setFont('Times',12);canvas.drawString(291,y,value)
    line('Hà Nội, tháng 11 năm 2026',82,12,True)
    canvas.restoreState()


def decorate(canvas,doc):
    if doc.page==1:
        cover(canvas);return
    canvas.saveState();canvas.setFont('Times',9)
    canvas.drawString(64,HEIGHT-36,'Giáp Minh Hiếu - B23DCCN299 | Project 01')
    canvas.drawCentredString(WIDTH/2,28,str(doc.page-1));canvas.restoreState()


class Thesis(BaseDocTemplate):
    def afterFlowable(self,flowable):
        if not hasattr(flowable,'style') or flowable.style.name not in ['h1','h2']:
            return
        title=flowable.getPlainText()
        if title=='MỤC LỤC':return
        key=f'heading-{self.seq.nextf("heading")}'
        self.canv.bookmarkPage(key)
        level=0 if flowable.style.name=='h1' else 1
        self.canv.addOutlineEntry(title,key,level=level,closed=False)
        self.notify('TOCEntry',(level,title,self.page-1,key))


def main():
    doc=Thesis(str(HERE/(STEM+'.pdf')),pagesize=A4,leftMargin=64,rightMargin=64,
        topMargin=57,bottomMargin=49,title='Project 01 - Phát triển hệ thống thông minh',
        author='Giáp Minh Hiếu',allowSplitting=1)
    frame=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id='normal',
                leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id='main',frames=frame,onPage=decorate))
    toc=TableOfContents()
    toc.levelStyles=[ParagraphStyle('toc1',fontName='Times-Bold',fontSize=11.2,leading=15.2,spaceBefore=7),
                     ParagraphStyle('toc2',fontName='Times',fontSize=10.7,leading=14.2,leftIndent=15,firstLineIndent=0)]
    contents=[Spacer(1,1),PageBreak(),fmt.para('MỤC LỤC','h1'),toc]
    order=json.loads((HERE/'section-order.json').read_text(encoding='utf-8'))
    for name in order:
        if name=='09-references.md':
            fmt.STYLES['body']=ParagraphStyle('reference-body',parent=fmt.STYLES['body'],fontSize=11,leading=14.5,spaceAfter=4,alignment=0)
        contents.extend(fmt.parse((HERE/'sections'/name).read_text(encoding='utf-8')))
    doc.multiBuild(contents,maxPasses=8)
    print(HERE/(STEM+'.pdf'))


if __name__=='__main__':main()
