from flask import Blueprint, redirect, render_template, request, send_file, url_for, current_app, send_from_directory
from flask_login import login_required
from io import BytesIO
from app.dao.common import get_doc_types
from app.dao.doc import get_docfiles_text, get_docfile_text, dbget_digfile_row
from app.main.doc import convert_html_to_pdf, get_docfile, get_docfiles, \
    docfile_create, upload_docfile, post_docfile, post_upload
from app.emails import app_send_email
import os

doc_bp = Blueprint('doc_bp', __name__)

@doc_bp.route('/docfile/<int:doc_id>', methods=['GET', 'POST'])
@login_required
def docfile(doc_id):
    if request.method == "POST":
        rent_id = post_docfile(doc_id)
        (url_for('rent_bp.rent', rent_id=rent_id))
    docfile, doc_dig = get_docfile(doc_id)
    doc_types = [typedoc.desc for typedoc in get_doc_types()]

    return render_template('docfile.html', docfile=docfile, doc_types=doc_types, doc_dig=doc_dig)


@doc_bp.route('/docfiles/<int:rent_id>', methods=['GET', 'POST'])
def docfiles(rent_id):
    docfiles, dfoutin = get_docfiles(rent_id)
    doc_types = [typedoc.desc for typedoc in get_doc_types()]
    outins = ["all", "out", "in"]

    return render_template('docfiles.html', rent_id=rent_id, dfoutin=dfoutin, docfiles=docfiles, doc_types=doc_types,
                           outins=outins)


@doc_bp.route('/docfiles_text/<int:rent_id>', methods=['GET', 'POST'])
def docfiles_text(rent_id):
    docfiles = get_docfiles_text(rent_id)

    return render_template('docfiles_text.html', docfiles=docfiles, rent_id=rent_id)


@doc_bp.route('/doc_print/<int:doc_id>', methods=['GET', 'POST'])
def doc_print(doc_id):
    try:
        docfile_text = get_docfile_text(doc_id)
        convert_html_to_pdf(docfile_text.doc_text, 'document.pdf')
        workingdir = os.path.abspath(os.getcwd())
        filepath = workingdir + '\\app\\temp_files\\'
        return send_from_directory(filepath, 'document.pdf')
    except Exception as ex:
        message = f'Unable to produce document. Error: {str(ex)}'

        return redirect(url_for('doc_bp.docfiles', rent_id=0, message=message))


@doc_bp.route('/download/<int:doc_id>')
@login_required
def download(doc_id):
    digfile = dbget_digfile_row(doc_id)

    return send_file(BytesIO(digfile.dig_data), attachment_filename=digfile.summary, as_attachment=True,
                     mimetype='application/pdf')


@doc_bp.route('/email_and_save', methods=['POST'])
def email_and_save():
    if request.method == "POST":
        # create the record to be uploaded to `docfile` table
        # this contains the email
        docfile = docfile_create(0)
        # send the email now, from the docfile record
        appmail = current_app.extensions['mail']
        recipients = request.form.get('email_to')
        subject = request.form.get('email_subject')
        html_body = docfile.doc_text
        # next line will raise an exception if there is a problem actually sending the email
        app_send_email(appmail, recipients, subject, html_body)
        # now upload to the database
        upload_docfile(docfile)
        rent_id = docfile.rent_id

        return redirect(url_for('doc_bp.docfiles', rent_id=rent_id))


@doc_bp.route('/upload_file/<int:rent_id>', methods=["GET", "POST"])
@login_required
def upload_file(rent_id):
    rentcode = request.args.get('rentcode', "dummy", type=str)
    if request.method == "POST":
        post_upload()
        return redirect('/rent/{}'.format(rent_id))
    doc_types = [typedoc.desc for typedoc in get_doc_types()]
    return render_template('upload_dialog.html', doc_types=doc_types, rentcode=rentcode, rent_id=rent_id)

# @doc_bp.route('/uploads/<filename>')
# def upload(filename):
#     return send_from_directory(app.config['UPLOAD_PATH'], filename)

