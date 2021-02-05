from flask import Blueprint, redirect, render_template, request, send_file, url_for
from flask_login import login_required
from io import BytesIO
from app.dao.doc_ import get_digfile, get_docfile, get_docfiles, post_docfile, post_upload
from app.dao.payrequest_ import post_new_payrequest

doc_bp = Blueprint('doc_bp', __name__)


@doc_bp.route('/docfile/<int:doc_id>', methods=['GET', 'POST'])
@login_required
def docfile(doc_id):
    if request.method == "POST":
        rent_id = post_docfile(doc_id)

        return redirect("/views/rent_/{}".format(rent_id))

    docfile, doc_dig = get_docfile(doc_id)

    return render_template('docfile.html', docfile=docfile, doc_dig=doc_dig)


@doc_bp.route('/docfiles/<int:rent_id>', methods=['GET', 'POST'])
def docfiles(rent_id):
    docfiles, dfoutin = get_docfiles(rent_id)
    outins = ["all", "out", "in"]

    return render_template('docfiles.html', rent_id=rent_id, dfoutin=dfoutin, docfiles=docfiles, outins=outins)


@doc_bp.route('/download/<int:doc_id>')
@login_required
def download(doc_id):
    digfile = get_digfile(doc_id)
    return send_file(BytesIO(digfile.dig_data), attachment_filename=digfile.summary, as_attachment=True,
                     mimetype='application/pdf')


@doc_bp.route('/save_html', methods=['GET', 'POST'])
def save_html():
    if request.method == "POST":
        id_ = post_docfile(0)
        return redirect(url_for('doc_bp.docfiles', rent_id=id_))


@doc_bp.route('/upload_file/<int:rent_id>', methods=["GET", "POST"])
@login_required
def upload_file(rent_id):
    rentcode = request.args.get('rentcode', "dummy", type=str)
    if request.method == "POST":
        post_upload()

        return redirect('/rent_/{}'.format(rent_id))

    return render_template('upload_dialog.html', rentcode=rentcode, rent_id=rent_id)

# @doc_bp.route('/uploads/<filename>')
# def upload(filename):
#     return send_from_directory(app.config['UPLOAD_PATH'], filename)

