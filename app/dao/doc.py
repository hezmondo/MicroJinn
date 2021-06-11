import imghdr
import os
from xhtml2pdf import pisa
from app import db
from flask import request
from sqlalchemy import desc, literal
from sqlalchemy.orm import load_only
from werkzeug.utils import secure_filename
from app.models import DigFile, DocFile, Rent, TypeDoc
from app.dao.database import commit_to_database


def allowed_filetypes():
    return ['.pdf', '.doc', '.docx', '.ods', '.odt', '.jpg', '.png', '.gif']


# Return the filepath of the pdf if success?
def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    workingdir = os.path.abspath(os.getcwd()) + '\\app\\temp_files\\'
    result_file = open(workingdir + output_filename, "w+b")
    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        source_html,  # the HTML to convert
        dest=result_file)  # file handle to recieve result
    # close output file
    result_file.close()  # close output file
    # return False on success and True on errors
    return pisa_status.err


def create_docfile_for_upload(doc_id):
    rent_id = int(request.form.get('rent_id'))
    doc_dig = request.form.get('doc_dig') or "doc"
    # new file for id 0, otherwise existing dig or doc file:
    if doc_id == 0:
        # new file has to be doc as new digital file uses upload function
        docfile = DocFile()
    else:
        docfile = DocFile.query.get(doc_id) if doc_dig == "doc" else DigFile.query.get(doc_id)
    docfile.rent_id = rent_id
    docfile.doc_date = request.form.get('doc_date')
    if doc_dig == "doc":
        docfile.doc_text = request.form.get('xinput').replace("£", "&pound;")
        # source_html = docfile.doc_text
        # output_filename = "{}-{}.pdf".format(docfile.summary, str(docfile.doc_date))
        # convert_html_to_pdf(source_html, output_filename)
    docfile.doctype_id = request.form.get('doctype_id')
    docfile.summary = request.form.get('summary')
    docfile.out_in = 0 if request.form.get('out_in') == "out" else 1
    return docfile


def get_digfile(doc_id):
    digfile = DigFile.query.filter(DigFile.id == doc_id).one_or_none()
    return digfile


def get_docfile(doc_id):
    doc_dig = request.args.get('doc_dig', "doc", type=str)
    rent_id = int(request.args.get('rent_id', "0", type=str))
    # new file has to be doc as new digital file uses upload function
    if doc_id == 0:
        docfile = DocFile()
        docfile.id = 0
        docfile.rent_id = int(rent_id)
        docfile.out_in = 1
        docfile.rentcode = Rent.query.with_entities(Rent.rentcode).filter(Rent.id == rent_id).one()[0]
        docfile.summary = "email in"
        docfile.doc_text = ""
        docfile.doctype_id = 1
    else:
        if doc_dig == "doc":
            docfile = DocFile.query \
                .join(Rent) \
                .join(TypeDoc) \
                .with_entities(DocFile.id, DocFile.summary, DocFile.out_in, DocFile.doc_text, DocFile.doc_date,
                            literal("doc").label('doc_dig'), Rent.rentcode, Rent.id.label("rent_id"), TypeDoc.desc) \
                .filter(DocFile.id == doc_id).one_or_none()
        else:
            docfile = DigFile.query.join(Rent).join(TypeDoc).with_entities(DigFile.id, DigFile.summary, DigFile.out_in,
                                                                           DigFile.doc_date,
                                                                           literal("dig").label('doc_dig'),
                                                                           Rent.rentcode, Rent.id.label("rent_id"),
                                                                           TypeDoc.desc) \
                .filter(DigFile.id == doc_id).one_or_none()
    return docfile, doc_dig


def get_docfiles(rent_id):
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
            digfile_filter.append(DigFile.summary.ilike('%{}%'.format(summary)))
            docfile_filter.append(DocFile.summary.ilike('%{}%'.format(summary)))
        if dftx and dftx != "":
            docfile_filter.append(DocFile.doc_text.ilike('%{}%'.format(dftx)))
        if dfty and dfty != "":
            digfile_filter.append(TypeDoc.desc.ilike('%{}%'.format(dfty)))
            docfile_filter.append(TypeDoc.desc.ilike('%{}%'.format(dfty)))
        if dfoutin == "out":
            digfile_filter.append(DigFile.out_in == 0)
            docfile_filter.append(DocFile.out_in == 0)
        elif dfoutin == "in":
            digfile_filter.append(DigFile.out_in == 1)
            docfile_filter.append(DocFile.out_in == 1)
    if rent_id > 0:
        digfile_filter.append(DigFile.rent_id == rent_id)
        docfile_filter.append(DocFile.rent_id == rent_id)

    docfiles = \
        DocFile.query \
            .join(Rent) \
            .join(TypeDoc) \
            .with_entities(DocFile.id, DocFile.doc_date, DocFile.summary, literal("doc").label('doc_dig'),
                           DocFile.doc_text.label('doctext'), DocFile.rent_id, TypeDoc.desc, DocFile.out_in, Rent.rentcode) \
            .filter(*docfile_filter).union \
            (DigFile.query \
             .join(Rent) \
             .join(TypeDoc) \
             .with_entities(DigFile.id, DigFile.doc_date, DigFile.summary, literal("dig").label('doc_dig'),
                            literal("Digitext").label('doctext'), DocFile.rent_id, TypeDoc.desc, DigFile.out_in, Rent.rentcode) \
             .filter(*digfile_filter)) \
            .order_by(desc(DocFile.doc_date), desc(DigFile.doc_date)).limit(100)
    return docfiles, dfoutin


def get_docfile_text(doc_id):
    return db.session.query(DocFile).filter_by(id=doc_id).options(load_only('doc_text')).one_or_none()


def get_docfiles_text(rent_id):
    return DocFile.query.filter_by(rent_id=rent_id)


def upload_docfile(docfile):
    db.session.add(docfile)
    commit_to_database()


def post_docfile(doc_id):
    docfile = create_docfile_for_upload(doc_id)
    upload_docfile(docfile)
    return docfile.rent_id


def post_upload():
    # new digital file uses upload function
    rent_id = int(request.form.get("rent_id"))
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
        digfile = DigFile()
        digfile.id = 0
        digfile.doc_date = doc_date
        digfile.summary = rentcode + '-' + filename
        digfile.dig_data = uploaded_file.read()
        digfile.doctype_id = \
            TypeDoc.query.with_entities(TypeDoc.id).filter(TypeDoc.desc == doctype).one()[0]
        digfile.rent_id = rent_id
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


