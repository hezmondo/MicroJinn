from flask import Blueprint, redirect, render_template, request, send_file
from flask_login import login_required
from io import BytesIO
from app.dao.doc_ import get_digfile, get_docfile, get_docfiles, post_docfile, post_payrequestfile, post_upload

doc_bp = Blueprint('doc_bp', __name__)


@doc_bp.route('/docfile/<int:id>', methods=['GET', 'POST'])
@login_required
def docfile(id):
    if request.method == "POST":
        rentid = post_docfile(id)

        return redirect("/views/rent_/{}".format(rentid))

    docfile, doc_dig = get_docfile(id)

    return render_template('docfile.html', docfile=docfile, doc_dig=doc_dig)


@doc_bp.route('/docfiles/<int:rentid>', methods=['GET', 'POST'])
def docfiles(rentid):
    docfiles, dfoutin = get_docfiles(rentid)
    outins = ["all", "out", "in"]

    return render_template('docfiles.html', rentid=rentid, dfoutin=dfoutin, docfiles=docfiles, outins=outins)


@doc_bp.route('/download/<int:id>')
@login_required
def download(id):
    digfile = get_digfile()
    return send_file(BytesIO(digfile.dig_data), attachment_filename=digfile.summary, as_attachment=True,
                     mimetype='application/pdf')


@doc_bp.route('/save_html', methods=['GET', 'POST'])
def save_html():
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        if action == "payrequest":
            id_ = post_payrequestfile()
        else:
            id_ = post_docfile(0)

        return redirect('/docfiles/{}'.format(id_))

        # return redirect('/docfile/{}?doc_dig_doc'.format(id_))


@doc_bp.route('/upload_file/<int:rentid>', methods=["GET", "POST"])
@login_required
def upload_file(rentid):
    rentcode = request.args.get('rentcode', "dummy", type=str)
    if request.method == "POST":
        post_upload()

        return redirect('/rent_/{}'.format(rentid))

    return render_template('upload_dialog.html', rentcode=rentcode, rent_id=rentid)

# @doc_bp.route('/uploads/<filename>')
# def upload(filename):
#     return send_from_directory(app.config['UPLOAD_PATH'], filename)

