from app import db
from flask import request
from sqlalchemy import desc, literal
from sqlalchemy.orm import load_only
from app.models import DigFile, DocFile, Rent, TypeDoc
from app.dao.database import commit_to_database


def dbget_digfile_row(digfile_id):
    return DigFile.query.get(digfile_id)


def dbget_docfile_row(docfile_id):
    return DocFile.query.get(docfile_id)


def dbget_docfiles_all():
    return db.session.query(DocFile).all()


def dbget_digfiles_all():
    return db.session.query(DigFile).all()


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


def dbget_docfiles(docfile_filter, digfile_filter):
    docfiles = \
        DocFile.query.join(Rent).join(TypeDoc) \
            .with_entities(DocFile.id, DocFile.doc_date, DocFile.summary, literal("doc").label('doc_dig'),
                           DocFile.doc_text.label('doctext'), DocFile.rent_id, TypeDoc.desc, DocFile.out_in, Rent.rentcode) \
            .filter(*docfile_filter) \
            .union_all(
            (DigFile.query.join(Rent).join(TypeDoc)
             .with_entities(DigFile.id, DigFile.doc_date, DigFile.summary, literal("dig").label('doc_dig'),
                            literal("Digitext").label('doctext'), DigFile.rent_id, TypeDoc.desc, DigFile.out_in, Rent.rentcode)
             .filter(*digfile_filter))) \
            .order_by(desc(DocFile.doc_date), desc(DigFile.doc_date)).limit(100)

    return docfiles


def get_docfile_text(doc_id):
    return db.session.query(DocFile).filter_by(id=doc_id).options(load_only('doc_text')).one_or_none()


def get_docfiles_text(rent_id):
    return DocFile.query.filter_by(rent_id=rent_id)


def get_typedoc_id(doctype):
    return TypeDoc.query.with_entities(TypeDoc.id).filter(TypeDoc.desc == doctype).one()[0]


def upload_docfile(docfile):
    db.session.add(docfile)
    commit_to_database()
