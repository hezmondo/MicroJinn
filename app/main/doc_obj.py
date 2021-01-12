import imghdr
import os
from xhtml2pdf import pisa
from app import db
from flask import flash, redirect, url_for, request, session
from sqlalchemy import and_, asc, desc, extract, func, literal, or_, text
from werkzeug.utils import secure_filename
from app.models import Digfile, Docfile, Rent, Typedoc



def get_docfile(id):
    doc_dig = request.args.get('doc_dig', "doc", type=str)
    rentid = int(request.args.get('rentid', "0", type=str))
    # new file has to be doc as new digital file uses upload function
    if id == 0:
        docfile = Docfile()
        docfile.id = 0
        docfile.rent_id = int(rentid)
        docfile.out_in = 1
        docfile.rentcode = Rent.query.with_entities(Rent.rentcode).filter(Rent.id == rentid).one()[0]
        docfile.summary = "email in"
        docfile.doc_text = ""
        docfile.doctype_id = 1
    else:
        if doc_dig == "doc":
            docfile = Docfile.query.join(Rent).join(Typedoc).with_entities(Docfile.id, Docfile.summary, Docfile.out_in,
                           Docfile.doc_text, Docfile.doc_date, literal("doc").label('doc_dig'),
                               Rent.rentcode, Rent.id.label("rent_id"), Typedoc.desc) \
                        .filter(Docfile.id == id).one_or_none()
        else:
            docfile = Digfile.query.join(Rent).join(Typedoc).with_entities(Digfile.id, Digfile.summary, Digfile.out_in,
                           Digfile.doc_date, literal("dig").label('doc_dig'),
                               Rent.rentcode, Rent.id.label("rent_id"), Typedoc.desc) \
                        .filter(Digfile.id == id).one_or_none()

    return docfile, doc_dig


def get_docfiles(rentid):
    digfile_filter = []
    docfile_filter = []
    dfoutin = "all"
    if request.method == "POST":
        rcd = request.form.get("rentcode") or ""
        summary = request.form.get("summary") or ""
        dftx = request.form.get("doc_text") or ""
        dfty = request.form.get("doc_type") or ""
        dfoutin = request.form.get("out_in") or ""
        if rcd and rcd != "":
            digfile_filter.append(Rent.rentcode.ilike('%{}%'.format(rcd)))
            docfile_filter.append(Rent.rentcode.ilike('%{}%'.format(rcd)))
        if summary and summary != "":
            digfile_filter.append(Digfile.summary.ilike('%{}%'.format(summary)))
            docfile_filter.append(Docfile.summary.ilike('%{}%'.format(summary)))
        if dftx and dftx != "":
            docfile_filter.append(Docfile.doc_text.ilike('%{}%'.format(dftx)))
        if dfty and dfty != "":
            digfile_filter.append(Typedoc.desc.ilike('%{}%'.format(dfty)))
            docfile_filter.append(Typedoc.desc.ilike('%{}%'.format(dfty)))
        if dfoutin == "out":
            digfile_filter.append(Digfile.out_in == 0)
            docfile_filter.append(Docfile.out_in == 0)
        elif dfoutin == "in":
            digfile_filter.append(Digfile.out_in == 1)
            docfile_filter.append(Docfile.out_in == 1)
    if rentid > 0:
        digfile_filter.append(Digfile.rent_id == rentid)
        docfile_filter.append(Docfile.rent_id == rentid)

    docfiles = \
        Docfile.query.join(Rent).join(Typedoc).with_entities(Docfile.id, Docfile.doc_date,
                    Docfile.summary, literal("doc").label('doc_dig'), Docfile.doc_text.label('doctext'),
                     Typedoc.desc, Docfile.out_in, Rent.rentcode) \
            .filter(*docfile_filter).union\
        (Digfile.query.join(Rent).join(Typedoc).with_entities(Digfile.id, Digfile.doc_date,
                    Digfile.summary, literal("dig").label('doc_dig'),
                      literal("Digitext").label('doctext'), Typedoc.desc, Digfile.out_in, Rent.rentcode) \
            .filter(*digfile_filter)) \
            .order_by(desc(Docfile.doc_date), desc(Digfile.doc_date)).limit(100)

    return docfiles, dfoutin


def post_docfile(id):
    rentid = int(request.form.get('rentid'))
    doc_dig = request.form.get('doc_dig') or "doc"
    # new file for id 0, otherwise existing dig or doc file:
    if id == 0:
        # new file has to be doc as new digital file uses upload function
        docfile = Docfile()
        docfile.id = 0
        docfile.rent_id = rentid
    else:
        docfile = Docfile.query.get(id) if doc_dig == "doc" else Digfile.query.get(id)
        docfile.rent_id = rentid
    docfile.doc_date = request.form.get('doc_date')
    if doc_dig == "doc":
        docfile.doc_text = request.form.get('xinput').replace("£", "&pound;")
        # source_html = docfile.doc_text
        # output_filename = "{}-{}.pdf".format(docfile.summary, str(docfile.doc_date))
        # convert_html_to_pdf(source_html, output_filename)
    doctype = request.form.get('doc_type')
    docfile.doctype_id = \
        Typedoc.query.with_entities(Typedoc.id).filter(Typedoc.desc == doctype).one()[0]
    docfile.summary = request.form.get('summary')
    docfile.out_in = 0 if request.form.get('out_in') == "out" else 1
    db.session.add(docfile)
    db.session.commit()
    return rentid


def post_upload():
    # new digital file uses upload function
    rentid = int(request.form.get("rentid"))
    rentcode = request.form.get("rentcode")
    doctype = request.form.get("doc_type")
    doc_date = request.form.get("doc_date")
    outin = request.form.get("out_in")
    uploaded_file = request.files.get('uploadfile')
    filename = secure_filename(uploaded_file.filename).lower()
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in allowed_filetypes():
            return "Invalid file suffix", 400
        elif file_ext in ['.jpg', '.png', '.gif'] and file_ext != validate_image(uploaded_file.stream):
            return "Invalid image", 400
        digfile = Digfile()
        digfile.id = 0
        digfile.doc_date = doc_date
        digfile.summary = rentcode + '-' + filename
        digfile.dig_data = uploaded_file.read()
        digfile.doctype_id = \
            Typedoc.query.with_entities(Typedoc.id).filter(Typedoc.desc == doctype).one()[0]
        digfile.rent_id = rentid
        digfile.out_in = 0 if outin == "out" else 1
        db.session.add(digfile)
        db.session.commit()
    # else:
    #     flash('No filename!')
    #     return redirect(request.url)


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


def allowed_filetypes():
    return ['.pdf', '.doc', '.docx', '.ods', '.odt', '.jpg', '.png', '.gif']


def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")
    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
            source_html,                # the HTML to convert
            dest=result_file)           # file handle to recieve result
    # close output file
    result_file.close()                 # close output file
    # return False on success and True on errors
    return pisa_status.err


